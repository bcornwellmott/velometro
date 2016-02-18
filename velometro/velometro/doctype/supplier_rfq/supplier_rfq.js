cur_frm.get_field('supplier_address').get_query = function(doc) {
	return {
		filters: {'supplier': doc.supplier}
	}
}

frappe.ui.form.on("Supplier RFQ", "refresh", function(frm) {
    if(cur_frm.doc.docstatus == 1){
	frm.add_custom_button(__("Create Supplier Quotation from RFQ"), function() {
        // When this button is clicked, do this
	
        	frappe.model.open_mapped_doc({
			method: "velometro.velometro.doctype.supplier_rfq.supplier_rfq.create_supplier_quotation",
			frm: cur_frm
		}) 				
	
    }); 
   }
});