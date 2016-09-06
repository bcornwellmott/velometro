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
	]
}
