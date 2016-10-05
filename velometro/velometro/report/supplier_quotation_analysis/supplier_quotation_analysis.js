// Copyright (c) 2016, Velometro Mobility Inc and contributors
// For license information, please see license.txt

frappe.query_reports["Supplier Quotation Analysis"] = {
	"filters": [
	{
		"fieldname":"supplier",
		"label": __("Supplier"),
		"fieldtype": "Link",
		"options": "Supplier",
		"default": "",
		"get_query": function() {
				return {
					filters: {"docstatus": ["<",2]}
				}
			}
		
		
	},{
		"fieldname":"supplier_quotation",
		"label": __("Supplier Quotation"),
		"fieldtype": "Link",
		"options": "Supplier Quotation",
		"default": "",
		"reqd": 1,
		"get_query": function() {
				var quote = frappe.query_report_filters_by_name.supplier.get_value();
				if (quote != "")
				{
					return {
						filters: {
							"supplier": quote,
							"docstatus" : 1
						}
					}
				}
				else{
					return {
						filters: {
							"docstatus" : 1
						}
					}
				}
				
			}
	}]
}
