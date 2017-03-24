# Copyright (c) 2017, ERPNext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.stock.doctype.item.item import get_last_purchase_details
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item

from frappe.utils import flt

def sum_bom_cost(item_list):
	total_cost = 0
	for item in item_list:
		total_cost += item.unit_cost * item.qty

	return total_cost
	
def get_item_cost(item_code, cost_method, qty):
	item_price = 0
	
	if cost_method == "Item Valuation Rate":
		# Get the item valuation method
		item_price == frappe.db.get_value("Bin",{"item_code": "item_code"}, "valuation_rate")

	elif cost_method == "Last Purchase Rate":
		last_purchase_details = get_last_purchase_details(item_code)
		item_price = last_purchase_details.base_rate
		
	elif cost_method == "Default Supplier":
	
		item = frappe.get_doc("Item", item_code)
		args = {
			"doctype": item.doctype,
			"name": item.name,
			"item_code": item.item_code, 
			"transaction_type": "buying",
			"supplier": item.default_supplier,
			"qty": qty
		}
		args = frappe._dict(args) 
		
		#frappe.msgprint(str(args))
		pr_price = 0		
		pr_result = get_pricing_rule_for_item(args) 
		if pr_result.pricing_rule:
			pricing_rule = frappe.get_doc("Pricing Rule", pr_result.pricing_rule)
			pr_price = pricing_rule.price 
		else:
			#Need to find the item price
			price_list = frappe.db.get_value("Supplier", item.default_supplier, "default_price_list")
			item_price = frappe.db.get_value("Item Price", {"price_list": price_list,"item_code": item.item_code}, "price_list_rate") or 0
	
		
	return item_price
	
@frappe.whitelist()
def solve_bom_cost(bom_name, primary_cost, secondary_cost, qty):
	item_list = []
	frappe.msgprint(str(bom_name))
	if bom_name:
		# Get the BOM 
		bom = frappe.get_doc("BOM", bom_name)
		if bom:
			# Get the pricing for each row
			for item in bom.items:
				# Find out the material request type
				mr_type = frappe.db.get_value("Item", item.item_code,"default_material_request_type")
				my_item = {}
				if mr_type == "Manufacture":
					# Check to see if there is a BOM and get the price of that BOM
					if item['bom_no']:
						my_item['unit_cost'] = sum_bom_cost(solve_bom_cost(item.bom_no, primary_cost, secondary_cost, item.qty * qty))
				else:
					# Go through the primary and secondary cost options
					my_item['unit_cost'] = get_item_cost(item.item_code, primary_cost, flt(item.qty) * flt(qty))
					if my_item['unit_cost'] == 0:
						my_item['unit_cost'] = get_item_cost(item.item_code, secondary_cost, flt(item.qty) * flt(qty))
						
				my_item['item_code'] = item.item_code
				my_item['bom_no'] = item.bom_no
				my_item['qty'] = item.qty
				my_item['uom'] = item.stock_uom
				my_item['item_name'] = item.item_name
				item_list.append(my_item)
				
			for op in bom.operations:
				my_item = {}
				my_item['unit_cost'] = op.hour_rate
				my_item['bom_no'] = ""
				my_item['item_code'] = op.operation
				my_item['qty'] = op.time_in_mins / 60
				my_item['uom'] = "Hours"
				my_item['item_name'] = op.description
				item_list.append(my_item)
	
	return item_list
	