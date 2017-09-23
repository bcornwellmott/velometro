// Copyright (c) 2016, Velometro Mobility Inc and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Yearly Summary"] = {
	"filters": [
	{
		"fieldname":"employee",
		"label": __("Employee"),
		"fieldtype": "Link",
		"options": "Employee",
		"default": ""
		
	},{
		"fieldname":"fiscal_year",
		"label": __("Fiscal Year"),
		"fieldtype": "Link",
		"options": "Fiscal Year",
		"default": ""
		
	}
	],
	"onload": function(frm) {
		if (frappe.user.has_role("HR Manager") || frappe.user.has_role("System Manager")) {
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
		}
	}
}
