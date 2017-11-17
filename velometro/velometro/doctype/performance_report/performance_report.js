// Copyright (c) 2017, Velometro Mobility Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Report', {
	refresh: function(frm) {

		frm.add_custom_button(__("Generate Employee Reports"), function(foo) {
				frm.call({
					method:"generate_reports"
				});
		});
	}
});

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	cur_frm.email_doc("");
}
