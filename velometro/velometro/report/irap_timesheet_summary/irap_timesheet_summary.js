// Copyright (c) 2019, Velometro Mobility Inc and contributors
// For license information, please see license.txt

frappe.query_reports["IRAP Timesheet Summary"] = {
	"filters": [
	{
		"fieldname":"start_date",
		"label": __("Start Date"),
		"fieldtype": "Date"
		
	},{
		"fieldname":"end_date",
		"label": __("End Date"),
		"fieldtype": "Date"
		
	}
	],
	"onload": function(frm) {
		/*if (frappe.user.has_role("HR Manager") || frappe.user.has_role("System Manager")) {
			frm.page.add_inner_button(__("Save All Employees"), function() {
				
				var args = {
					cmd: 'velometro.velometro.report.employee_yearly_summary.employee_yearly_summary.export_all',
					report_name: "Employee Yearly Report",
					file_format_type: "Excel",
					employee: frm.filters[0].value,
					year: frm.filters[1].value
				}
				
				open_url_post(frappe.request.url, args);

			});
		}*/
	}
}
