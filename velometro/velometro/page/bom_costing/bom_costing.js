frappe.pages['bom-costing'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'BOM Costing',
		single_column: true
	});
	
	new erpnext.BOMCosting(wrapper);

	frappe.breadcrumbs.add("Manufacturing");
}

erpnext.BOMCosting = frappe.views.GridReport.extend({
	init: function(wrapper) {
		this._super({
			title: __("BOM Costing"),
			page: wrapper,
			parent: $(wrapper).find('.layout-main'),
			page: wrapper.page
		});

	},
	setup_columns: function() {
		console.log("setup_columns");
		var std_columns = [
			{id: "check", name: "Plot", field: "check", width: 60, hidden: 0,
				formatter: this.check_formatter},
			{id: "item_code", name: "Item Code", field: "item_code", width: 100, hidden: 0,
				formatter: this.text_formatter},
			{id: "item_name", name: "Name", field: "name", width: 300, hidden: 0,
				formatter: this.text_formatter},
			{id: "bom_no", name: "BOM No", field: "bom_no", width: 50, hidden: 1,
				formatter: this.text_formatter},
			{id: "qty", name: "Quantity", field: "qty", plot: false, hidden: 0,
				formatter: this.currency_formatter},
			{id: "unit", name: "UOM", field: "unit", plot: false, hidden: 0,
				formatter: this.text_formatter},
			{id: "item_price", name: "Item Price", field: "item_price", plot: false, hidden: 0,
				formatter: this.currency_formatter},
			{id: "sum_price", name: "Total Price", field: "sum_price", plot: true, hidden: 0,
				formatter: this.currency_formatter}
		];

		this.columns = std_columns;
	},
	filters: [
			
		{fieldtype:"Link", fieldname: "bom", label: __("BOM"),  link:"BOM"},
		{fieldtype:"Select", fieldname: "primary_pricing", label:  __("Primary Pricing Based On"),	
			options:[{label: __("Item Valuation Rate"), value: "Item Valuation Rate"}, {label: __("Last Purchase Rate"), value: "Last Purchase Rate"},{label: __("Default Supplier"), value: "Default Supplier"}]},		
		{fieldtype:"Select", fieldname: "secondary_pricing", label:  __("Backup Pricing Based On"),	
			options:[{label: __("Item Valuation Rate"), value: "Item Valuation Rate"},{label: __("Last Purchase Rate"), value: "Last Purchase Rate"},{label: __("Default Supplier"), value: "Default Supplier"}]},		
		{fieldtype:"Data", fieldname: "quantity", label: __("Build Quantity"), "default": 1}
	],
	setup_filters: function() {
		console.log("setup_filters");
		var me = this;
		this._super();

		this.trigger_refresh_on_change(["bom", "quantity"]);
		
		
	},
	init_filter_values: function() {
		console.log("init_filter_values");
		
		var me = this;
		
		
		this._super();
		this.filter_inputs.primary_pricing.val('Item Valuation Rate');
		this.filter_inputs.secondary_pricing.val('Last Purchase Rate');
		this.filter_inputs.quantity.val('1');
		
		
		
		
	},	
	get_data: function(callback) {
		console.log("get_data");
		var me = this;

		if(!me.setup_filters_done) {
				me.setup_filters();
				me.setup_filters_done = true;
			}
				
		if (this.filter_inputs.bom.val() != ""){
		
			var bname = this.filter_inputs.bom.val();
			var prim = this.filter_inputs.primary_pricing.val();
			var secd = this.filter_inputs.secondary_pricing.val();
			var quant = this.filter_inputs.quantity.val();
			var opts = {
					bom_name: bname,
					primary_cost: prim,
					secondary_cost: secd, 
					qty: quant
				};
			var me = this;
			frappe.call({
				method: "velometro.velometro..page.bom_costing.bom_costing.solve_bom_cost",
				args: opts,
				freeze: true,
				callback: function(r) {
					//Load the data into columns
					console.log(r);
					me.raw_data = r.message;
					callback();
				}
				});
		}
	},
	prepare_data: function() {
		var me = this;

		console.log("prepare_data");
		this.data = [];
		var me = this;
		$.each(this.raw_data, function(i, d) { 
			var new_row = [];
			new_row.item_code = d.item_code;
			new_row.qty = d.qty;
			new_row.item_price = d.unit_cost;
			new_row.name = d.item_name;
			new_row.bom_no = d.bom_no;
			new_row.unit = d.uom;
			new_row.checked = true;
			new_row.id = i;
			var total =  d.qty * d.unit_cost;
			new_row.sum_price = total;
			me.data.push(new_row);
		});
		
	},
	prepare_data_view: function () {
		
		console.log("prepare_data_view");
		//initialize the model
		this.dataView = new Slick.Data.DataView({ inlineFilters: true });
		this.dataView.beginUpdate();
		this.dataView.setItems(this.data);
		if(this.dataview_filter) this.dataView.setFilter(this.dataview_filter);
		if(this.tree_grid.show) this.dataView.setFilter(this.tree_dataview_filter);
		this.dataView.endUpdate();
	},
	setup_chart: function() {
		console.log("setup_chart");
		var me = this;
		var chart_data = this.get_chart_data ? this.get_chart_data() : null;

		console.log(chart_data);
		this.chart = new frappe.ui.Chart({
			wrapper: this.chart_area,
			data: chart_data,
			chart_type: 'pie',
		});
		
	},
	get_chart_data: function() {
		var me = this;
		console.log("get_chart_data");

		var plottable_cols = [];
		console.log(me.data);
		
		var me = this;
		var data = {
			'columns':[],
			onclick: function (d, i) { 
				console.log(me.data[d.index]);
				if (me.data[d.index].bom_no)
				{
					me.filter_inputs.bom.val(me.data[d.index].bom_no);
					me.get_data_and_refresh();
				}
			}
		};
		
		$.each(this.data, function(i, item) {
			console.log('item');
			console.log(item);
			if (item.checked) {
				var item_points = [item.item_code];
				item_points.push(item.sum_price);
				data['columns'].push(item_points);
			}
		});
		return data
	},
	make_filters: function() {
		var me = this;
		$.each(this.filters, function(i, v) {
			v.fieldname = v.fieldname || v.label.replace(/ /g, '_').toLowerCase();
			var input = null;
			if(v.fieldtype=='Select') {
				input = me.page.add_select(v.label, v.options || [v.default_value]);
			} else if(v.fieldtype=="Link") {
				input = me.page.add_data(v.label);
				input.autocomplete({
					source: v.list || [],
				});
			} else if(v.fieldtype==='Button' && v.label===__("Refresh")) {
				input = me.page.set_primary_action(v.label, null, v.icon);
			} else if(v.fieldtype==='Button') {
				input = me.page.add_menu_item(v.label, null, true);
			} else if(v.fieldtype==='Date') {
				input = me.page.add_date(v.label);
			} else if(v.fieldtype==='Label') {
				input = me.page.add_label(v.label);
			} else if(v.fieldtype==='Data') {
				input = me.page.add_data(v.label);
			} else if(v.fieldtype==='Check') {
				input = me.page.add_check(v.label);
			}

			if(input) {
				input && (input.get(0).opts = v);
				if(v.cssClass) {
					input.addClass(v.cssClass);
				}
				/*input.keypress(function(e) {
					if(e.which==13) {
						me.refresh();
					}
				})*/
			}
			me.filter_inputs[v.fieldname] = input;
		});
	}
	
});