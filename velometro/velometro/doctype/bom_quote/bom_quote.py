# -*- coding: utf-8 -*-
# Copyright (c) 2015, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc 
from frappe.model.meta import get_field_currency
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item
from frappe.defaults import get_user_default 
from erpnext.setup.utils import get_exchange_rate
import json

class BOMQuote(Document): 
	
	def validate(self):

		unit_pcost = 0 
		total_time = 0 
		unit_acost = 0
		self.master_item = frappe.get_value("BOM", self.master_bom, "item")
		self.description = frappe.get_value("Item", self.master_item, "description")
		self.currency = frappe.get_value("Company", self.company, "default_currency")

		bom_doc = frappe.get_doc("BOM", self.master_bom)
		 
		item_list = []

		for purchased in self.items:
			item_list.append(purchased.item)

		for exp_item in bom_doc.exploded_items:
			if not exp_item.item_code in item_list: 

				doc = frappe.new_doc("BOM Costing Purchased Item", bom_doc, "items") 
				doc.item = exp_item.item_code 
				doc.supplier = frappe.get_value("Item",doc.item,"default_supplier")
				doc.price_list =  frappe.get_value("Item",doc.item,"default_supplier")
				doc.currency = frappe.get_value("Supplier", doc.supplier,"default_currency") 
				doc.description = exp_item.description 
				doc.item_name= exp_item.item_name
				doc.qty_per_asm= exp_item.qty
				doc.idx = None
				self.append("items",doc)

		for purchased in self.items:
			purchased.qty = self.quantity * purchased.qty_per_asm  
			purchased.purchase_rate = get_item_price(purchased, self.company)
			if not purchased.taxes:
				purchased.taxes = 0 
			if not purchased.freight:
				purchased.freight = 0

			fields = ["purchase_rate", "taxes", "freight"]
			from_currency = purchased.currency
			to_currency = self.currency
			conversion_rate = get_exchange_rate(from_currency, to_currency)
			for f in fields:
				
				val = flt(flt(purchased.get(f), purchased.precision(f)) * conversion_rate, purchased.precision("base_" + f))
				purchased.set("base_" + f, val) 

			purchased.unit_price = purchased.purchase_rate + purchased.taxes + purchased.freight
			purchased.base_unit_price = purchased.base_purchase_rate + purchased.base_taxes + purchased.base_freight
			purchased.total_price = purchased.base_unit_price * purchased.qty_per_asm
			unit_pcost = unit_pcost  + (purchased.base_unit_price * purchased.qty_per_asm)

		bom_list = [self.master_bom]
		bom_list = get_boms_list(self.master_bom, bom_list) 

		bom_operations = []
		for bo in self.operations:
			bom_operations.append(bo.bom)

			if bo.bom in bom_list:
				#Update the BOM operation
				child_operation = get_bom_operation(bo.bom)
				bo.minutes = child_operation.minutes
				bo.num_operators = child_operation.num_operators
				bo.total_cost = child_operation.total_cost
				bo.operations = child_operation.operations 


		for boma in bom_list:
			if not boma in bom_operations: 

				child_operation = get_bom_operation(boma)
				self.append("operations",child_operation)


		for ops in self.operations:
				total_time = total_time + ops.minutes
				unit_acost = unit_acost + ops.total_cost

		self.assembly_time = total_time 
		self.assembly_cost = unit_acost
		
		self.purchased_cost = unit_pcost
		self.unit_cost = self.purchased_cost + self.assembly_cost 
		self.total_cost = self.quantity * self.unit_cost 
 
@frappe.whitelist() 
def load_bom(source_name, target_doc = None): 
	"""Loads the BOM items into the BOM Costing form""" 
	

	#frappe.msgprint("{0}".format(target_doc)) 
	quantity = 0 
	company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")

	if target_doc:
		args = frappe._dict(json.loads(target_doc)) 
		if args.quantity:
			quantity = args.quantity
		if args.company:
			company = args.company 
		
	
	def postprocess(source,target):
		# Set the supplier information
		
		frappe.msgprint("Completed Loading")
		
	def process_item(obj, target, source_parent):
		item_doc = frappe.get_doc("Item",obj.item_code)
		target.supplier = item_doc.default_supplier
		target.price_list = item_doc.default_supplier
		target.currency = frappe.get_value("Supplier", target.supplier,"default_currency") 
		target.qty = target.qty_per_asm * quantity
		target.purchase_rate = get_item_price(target, company)

	
	#frappe.msgprint("Vehicle Quantity: {0}".format(quantity))
	#frappe.msgprint("Company: {0}".format(company))
	doc= get_mapped_doc("BOM", source_name,{ 
		"BOM": { 
			"doctype": "BOM Quote",
			"field_map": {
				"item": "master_item",	
				"company": "company"	 	
			}
			
		},
		"BOM Explosion Item": {
			"doctype": "BOM Costing Purchased Item",
			"field_map": {
				"item_code": "exp_item",
				"description": "description",
				"item_name": "item_name",
				"qty": "qty_per_asm" 
			},
			"postprocess": process_item 
		}}, target_doc,postprocess)
	

	return doc

def get_item_price(item, company):
	"""Gets the item price from the price list taking in the total number of assemblies being made and name of the company"""

	#Get the Item 
	item_doc = frappe.get_doc("Item",item.item)

	total_qty = item.qty
	args = {
		"doctype": item.doctype,
		"parent_type": item.parenttype,
		"name": item_doc.name,
		"item_code": item.item, 
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
	if pr_result.pricing_rule:
		pricing_rule = frappe.get_doc("Pricing Rule", pr_result.pricing_rule)
		pr_price = pricing_rule.price 
	else:
		#Need to find the item price
		pr_price = frappe.db.get_value("Item Price", {"price_list": item.price_list,"item_code": item.item}, "price_list_rate") or 0


	#frappe.msgprint("Price: {0}".format(pr_price))
	#frappe.msgprint("Pricing Rule: {0}".format(pr_result.pricing_rule))
	return pr_price 

def get_taxes_charges(item, type, company):
	#Get the Item 
	item_doc = frappe.get_doc("Item",item.item)

	total_qty = item.qty
	args = {
		"doctype": item.doctype,
		"parent_type": item.parenttype,
		"name": item_doc.name,
		"item_code": item.item, 
		"transaction_type": "buying",
		"supplier": item.supplier,
		"qty": item.qty,
		"price_list": item.price_list, 
		"company": company
	}

	#frappe.msgprint("{0}".format(args))
	args = frappe._dict(args) 

	pr_price = 0		

	# Get the pricing rule
	pr_result = get_pricing_rule_for_item(args) 
	if pr_result.pricing_rule:
		pricing_rule = frappe.get_doc("Pricing Rule", pr_result.pricing_rule)
		
		# Find the supplier quotation associated with this pricing rule
		quotation = frappe.get_doc("Supplier Quotation", pricing_rule.from_supplier_quotation)

		# Get the master quote quantity based on our total quantity for this part
		qtylist = [] 	
		for item in quotation.items:
			if item.item_code == pricing_rule.item_code:
				qtylist.append(item.qty)
		qtylist.sort()
		count = 0 
		for i in qtylist: 
			count = count + 1
			if i == pricing_rule.min_qty:
				break
			

		if count > 0:
			# Loop through each charge type to find the one with the correct quantity and type
			applicable_charges = []
			for tax_charge in quotation.taxes:
				desc_list = "{" + tax_charge.description + "}"
				#frappe.msgprint("{0}".format(desc_list))
				args = frappe._dict(json.loads(desc_list))
				if args.type == type:
					applicable_charges.append(args.qty)
			applicable_charges.sort()
			for tax_charge in quotation.taxes:
				desc_list = "{" + tax_charge.description + "}"
				args = frappe._dict(json.loads("{" + desc_list + "}"))
				if args.type == type and args.qty == applicable_charges[count-1]:
					# We finally found the correct charge for freight
					#frappe.msgprint("{0}".format(tax_charge.price))
					return tax_charge.price
		
	else:
		#Need to find the item price
		return 0



def get_bom_operation(bom):
	
	bom_doc = frappe.get_doc("BOM", bom) 
	atime = 0
	cost = 0
	num_operators = 0
	operations = []

	if bom_doc.with_operations:
		for op in bom_doc.operations:
			atime = atime + op.time_in_mins 
			cost = cost + op.operating_cost 
			num_operators = num_operators + 1
			operations.append(op.operation)
	
	doc = frappe.new_doc("BOM Costing Operations", bom_doc, "operations") 
	doc.minutes = atime
	doc.num_operators = num_operators
	doc.total_cost = cost
	doc.bom = bom_doc.name 
	doc.operations = ", ".join(filter(None, operations))
	doc.idx = None
	#{"doctype":"BO Costing Operations", "minutes": time, "num_operators": num_operators, "total_cost": cost, "parent": bom_doc.name, "parentfield": "operations", "parenttype":"BOM Quote"})

	return doc
	
def get_boms_list(parent_bom,bom_list = []):
	bom = frappe.get_doc("BOM", parent_bom)

	for bom_item in bom.items: 
		has_bom = bom_item.bom_no
		if has_bom:
			bom_list.append(has_bom)
			bom_list = get_boms_list(has_bom, bom_list)
		
	return bom_list
	
