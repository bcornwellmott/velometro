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


frappe.ui.form.on('BOM Quote', "load_bom_button", function(frm){
	
	frm.call({
		'method': 'load_bom',
		'doc':frm.doc,		
		'callback': function() {
			frm.reload_doc();
		}
	});
	 frm.set_df_property("master_bom", "read_only", 1);
	 frm.set_df_property("quantity", "read_only", 1);
	 frm.set_df_property("load_bom_button", "hidden", 1);

});





