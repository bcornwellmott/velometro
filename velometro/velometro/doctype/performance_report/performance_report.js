// Copyright (c) 2017, Velometro Mobility Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Report', {
	refresh: function(frm) {
		var me = this;
		frm.add_custom_button(__("Generate Employee Reports"), function() {
				frm.call({
					method:"generate_reports"
				});
		});
		
		if(!cur_frm.doc.meeting && frm.doc.docstatus == 1)
		{
			frm.add_custom_button(__("Create Review Meeting"), function() {
				cur_frm.doc.meeting_check = 1;
				make_performance_meeting();
			});
		}
		

	},
	
	
});

function make_performance_meeting() {
		frappe.call({
			method:"velometro.velometro.doctype.performance_report.performance_report.make_performance_meeting",
			args: {
				performance_report: cur_frm.doc.name
			},
			callback: function(r) {
				var doclist = frappe.model.sync(r.message);
				cur_frm.doc.meeting = doclist[0].name;
				cur_frm.save('Update', null, this);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		});
	}
cur_frm.add_fetch('employee','employee_name','employee_name');
cur_frm.add_fetch('manager','employee_name','manager_name');


cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	cur_frm.email_doc("Hello, \nPlease review this performance evaluation prepared by your peers for the past week. If you have any issues you'd like to discuss, please let me know.");
}
