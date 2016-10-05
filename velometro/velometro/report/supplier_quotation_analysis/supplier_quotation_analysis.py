# Copyright (c) 2013, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item
from frappe.utils import flt
import frappe

def execute(filters=None):
	
	itemqty_list = get_itemquantity_list(filters.supplier_quotation)
	
	data = get_item_list(filters.supplier_quotation, itemqty_list)
	
	columns = get_columns(itemqty_list, filters.supplier)
	
	return columns, data

	
def get_item_list(quote, qty_list):
	
	out = []
	
	if quote:
		low_price_data = []
		low_supplier = []
		company = frappe.db.get_default("company")
		company_currency = frappe.db.get_default("currency")
		# Get the default supplier of suppliers

			
		#Add a row for each item/qty
		for root in qty_list:
			root.supplier = frappe.db.get_value("Item", root.item_code,"default_supplier")
			root.price_list = frappe.db.get_value("Supplier", root.supplier,"default_price_list")
			supplier_currency = frappe.db.get_value("Supplier", root.supplier,"default_currency")
			price = get_item_price(root,company)
				
			exg = get_exchange_rate(supplier_currency,company_currency) or 1
			
			percent = flt(100*(root.rate - price * exg) / price)
			
			row = frappe._dict({
				"line_item": root.label,
				"supplier_price": root.rate,
				"lowest_price": price * exg,
				"lowest_supplier": root.supplier,
				"percent_diff": percent
			})
			out.append(row)

	return out
	
def get_itemquantity_list(item):
	
	out = []
	
			
	if item:
		qty_list = frappe.db.sql("""select item_code, qty, rate from `tabSupplier Quotation Item` as item where parent =%s and docstatus = 1""", item, as_dict=1)
		qty_list.sort(reverse=False)
		for qt in qty_list:
			col = frappe._dict({
				"key": str(qt.item_code) + " x" + str(qt.qty),
				"item_code": qt.item_code,
				"qty": qt.qty,
				"rate": qt.rate,
				"label": str(qt.item_code) + " x" + str(qt.qty)
			})
			out.append(col)

	return out
	
def get_columns(qty_list, supplier):
	columns = [{
		"fieldname": "line_item",
		"label": "Item & QTY",
		"fieldtype": "Data",
		"options": "",
		"width": 200
	},{
		"fieldname": "supplier_price",
		"label": supplier + " Price",
		"fieldtype": "Currency",
		"options": "",
		"width": 120
	},{
		"fieldname": "lowest_price",
		"label": "Lowest Price",
		"fieldtype": "Currency",
		"options": "",
		"width": 120
	},{
		"fieldname": "lowest_supplier",
		"label": "Lowest Supplier",
		"fieldtype": "Data",
		"options": "",
		"width": 200
	},{
		"fieldname": "percent_diff",
		"label": "% Difference",
		"fieldtype": "Percent",
		"options": "",
		"width": 120
	},]

	return columns
	
def get_item_price(item, company):
	"""Gets the item price from the price list taking in the total number of assemblies being made and name of the company"""
	#frappe.msgprint(str(item))
	#Get the Item 
	item_doc = frappe.get_doc("Item",item.item_code)

	total_qty = item.qty
	args = {
		"doctype": "Item",
		"name": item_doc.item_code,
		"item_code": item.item_code, 
		"transaction_type": "buying",
		"supplier": item.supplier,
		"qty": item.qty,
		"price_list": item.price_list, 
		"company": company
	}

	#frappe.msgprint("{0}".format(args))
	args = frappe._dict(args) 

	pr_price = 0		

	pr_result = get_pricing_rule_for_item(args) 
	
	#frappe.msgprint(str(pr_result))
	
	
	if pr_result.pricing_rule:
		pricing_rule = frappe.get_doc("Pricing Rule", pr_result.pricing_rule)
		pr_price = pricing_rule.price 
	else:
		#Need to find the item price
		pr_price = frappe.db.get_value("Item Price", {"price_list": item.price_list,"item_code": item.item}, "price_list_rate") or 0


	#frappe.msgprint("Price: {0}".format(pr_price))
	#frappe.msgprint("Pricing Rule: {0}".format(pr_result.pricing_rule))
	return pr_price 