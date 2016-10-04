// Copyright (c) 2016, Velometro Mobility Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOM Quote', {
	validate: function(frm) {
		frm.doc.prep_date = get_today();
	
	},
	refresh: function(frm) {
		if (frm.doc.master_bom){
			frm.set_df_property("master_bom", "read_only", 1);
		}
	} 
});


frappe.ui.form.on('BOM Quote', "master_bom", function(frm){
	/*console.log("TEST")
	erpnext.utils.map_current_doc({
		method: "velometro.velometro.doctype.bom_quote.bom_quote.load_bom",
		frm: cur_frm,
		source_name: frm.doc.master_bom
	});
	cur_frm.reload_doc();
	frm.call({
		'method': 'frappe.client.get',
		'args': {
			 'doctype': 'BOM',
          		'name':frm.doc.master_bom			
		},
		'callback': function(item) {

			frappe.model.set_value(frm.doctype,frm.docname,"master_item",item.message.item);
			frm.call({
				'method': 'frappe.client.get',
				'args': {
				 'doctype': 'Item',
        		  		'name':item.message.item				
				},	
				'callback': function(item) {
					frappe.model.set_value(cur_frm.doctype,cur_frm.docname,"item_description",item.message.description);
					
		
				}
		});


		}
	});*/
	 frm.set_df_property("master_bom", "read_only", 1);


	
 
});





