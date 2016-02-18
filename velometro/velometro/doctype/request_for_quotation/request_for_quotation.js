frappe.ui.form.on("RFQ Item", {

	item: function(frm, cdt, cdn) {
		var item = frappe.model.get_doc(cdt,cdn);
		if(item.item) {

			frm.call({
				'method': 'frappe.client.get',
				'args': {
					 'doctype': 'Item',
            				'name':locals[cdt][cdn].item				
				},
				'callback': function(item) {
					frappe.model.set_value(cdt,cdn,"description",item.message.description);
					frappe.model.set_value(cdt,cdn,"revision",item.message.revision);
					frappe.model.set_value(cdt,cdn,"supplier_code","");

				}
			});
			frm.call({
				'method': 'velometro.velometro.doctype.request_for_quotation.request_for_quotation.get_item_attachments',
				'args': {
					 'item_code':locals[cdt][cdn].item				
				},
				'callback': function(message) {
					frappe.model.set_value(cdt,cdn,"include_pdf",message.message.include_pdf);
					frappe.model.set_value(cdt,cdn,"include_stp",message.message.include_stp);
					frappe.model.set_value(cdt,cdn,"include_xt",message.message.include_xt);
					frappe.model.set_value(cdt,cdn,"include_dxf",message.message.include_dxf);
					console.log(message);
					

				}
			});

		}
		else {
			frappe.model.set_value(cdt,cdn,"description",null);
			frappe.model.set_value(cdt,cdn,"qty",0);
			frappe.model.set_value(cdt,cdn,"supplier_code",null);
		}
	}
})

cur_frm.add_fetch("company", "address","company_address")

frappe.ui.form.on("Request for Quotation", {

	
	company: function(frm, company) {

		

			}
})

cur_frm.fields_dict['suppliers'].grid.get_field('contact').get_query = function(doc, cdt, cdn) {
	return {
		filters: {'supplier': locals[cdt][cdn].supplier}
	}
}


