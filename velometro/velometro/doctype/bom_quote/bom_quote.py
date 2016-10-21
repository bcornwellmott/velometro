# -*- coding: utf-8 -*-
# Copyright (c) 2015, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import bisect
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc 
from frappe.model.meta import get_field_currency
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item
from frappe.defaults import get_user_default 
from erpnext.setup.utils import get_exchange_rate
import json

class BOMQuote(Document): 
	
	# Go through each item in this BOM

	def validate(self):
		
		if len(self.items) == 0:
			self.load_bom()
		else:
			self.update_item_prices()
		
	def update_item_prices(self):
		unit_pcost = 0 
		total_time = 0 
		unit_acost = 0
		for purchased in self.items:
			purchased.qty = purchased.qty_per_asm  * self.quantity
			purchased.purchase_rate = get_item_price(purchased, self.company)
			if not purchased.taxes:
				purchased.taxes = 0 
				if not purchased.freight:
					purchased.freight = 0
				fields = ["purchase_rate", "taxes", "freight"]
				from_currency = purchased.currency
				to_currency = self.currency
				conversion_rate = get_exchange_rate(from_currency, to_currency)
				if not conversion_rate:
					conversion_rate = 0
				#frappe.msgprint(conversion_rate)
				for f in fields:
					val = flt(flt(purchased.get(f), purchased.precision(f)) * conversion_rate, purchased.precision("base_" + f))
					purchased.set("base_" + f, val) 
					
				purchased.unit_price = purchased.purchase_rate + purchased.taxes + purchased.freight
				purchased.base_unit_price = purchased.base_purchase_rate + purchased.base_taxes + purchased.base_freight
				purchased.total_price = purchased.base_unit_price * purchased.qty_per_asm
				unit_pcost = unit_pcost  + (purchased.base_unit_price * purchased.qty_per_asm)
		
		for operations in self.operations:
			total_time += operations.minutes
			unit_acost += operations.total_cost
			
		self.assembly_time = total_time 
		self.assembly_cost = unit_acost
		
		self.purchased_cost = unit_pcost
		self.unit_cost = self.purchased_cost + self.assembly_cost  
		self.total_cost = self.quantity * self.unit_cost 

	
	def load_bom(self):
		if not hasattr(self,"items"):
			self.items = []
		if not hasattr(self,"operations"):
			self.operations = []
		add_bom_level(self, 1, self.master_bom)
		
		#Sort by item code and reassign idx
		self.items.sort(key=getKey)
		idx = 1
		for itm in self.items:
			itm.idx = idx
			itm.parent = self.name
			itm.parenttype = "BOM Quote"
			idx += 1
			
		#Sort by bom_no and reassign idx
		self.operations.sort( key=getKey)
		idx = 1
		for itm in self.operations:
			itm.idx = idx
			itm.parent = self.name
			itm.parenttype = "BOM Quote"
			idx += 1
		self.update_item_prices()
		
	
def getKey(item):
	return item.sort_name

	
def add_bom_level(doc, qty, bom):
	# Get the BOM doc
	#frappe.msgprint("Getting BOM for" + bom)
	bom_doc = frappe.get_doc("BOM",bom)
	
	#Add the operations from this BOM to the list
	new_operation = get_bom_operation(bom, qty)
	new_operation.idx = len(doc.operations)+1
	doc.operations.append(new_operation)
	
	#Go through each item in the BOM to decide if it is a Purchased or Manufactured item
	for myItem in bom_doc.items:
		item_quantity = qty * myItem.qty  
		item_doc = frappe.get_doc("Item",myItem.item_code)
		if myItem.bom_no and item_doc.default_material_request_type == "Manufacture":
			# This is a manufactured item and we should add it to the BOM Operations then scan it's children
			add_bom_level(doc,item_quantity, myItem.bom_no)
		else:
			# Consider it a purchased item, and just set the basics (Item Code, Qty, Supplier, Currency, Price List)
			#frappe.msgprint("Getting BOM for" + bom)
			new_purchased = get_purchase_item(myItem.item_code, item_quantity)
			new_purchased.idx = len(doc.items)+1
			bisect.insort_left(doc.items,new_purchased)		
			
def get_purchase_item(item_code,qty):
	doc = frappe.new_doc("BOM Costing Purchased Item") 
	doc.item = item_code
	doc.sort_name = item_code.lower()
	doc.supplier = frappe.get_value("Item",doc.item,"default_supplier")
	doc.price_list =  frappe.get_value("Item",doc.item,"default_supplier")
	doc.currency = frappe.get_value("Supplier", doc.supplier,"default_currency") 
	doc.description = frappe.get_value("Item",doc.item,"description")
	doc.item_name= frappe.get_value("Item",doc.item,"item_name")
	doc.qty_per_asm= qty
	doc.idx = None
	return doc
	
def get_bom_operation(bom, qty):
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
	
	doc = frappe.new_doc("BOM Costing Operations") 
	doc.minutes = atime
	
	doc.num_operators = num_operators
	doc.total_cost = cost * qty
	doc.bom = bom_doc.name 
	doc.sort_name = bom.lower()
	doc.operations = ", ".join(filter(None, operations))
	doc.idx = None
	return doc
	
def get_item_price(item, company):
	"""Gets the item price from the price list taking in the total number of assemblies being made and name of the company"""
	
	#Get the Item 
	item_doc = frappe.get_doc("Item",item.item)

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
	args = frappe._dict(args) 
	
	#frappe.msgprint(str(args))
	pr_price = 0		
	pr_result = get_pricing_rule_for_item(args) 
	if pr_result.pricing_rule:
		#frappe.msgprint("Found pricing rule for " + item.item + ": " + pr_result.pricing_rule)
		pricing_rule = frappe.get_doc("Pricing Rule", pr_result.pricing_rule)
		pr_price = pricing_rule.price 
	else:
		#Need to find the item price
		#frappe.msgprint("Could not find pricing rule for " + item.item )
		pr_price = frappe.db.get_value("Item Price", {"price_list": item.price_list,"item_code": item.item}, "price_list_rate") or 0
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
				args = frappe._dict(json.loads(desc_list))
				if args.type == type:
					applicable_charges.append(args.qty)
			applicable_charges.sort()
			for tax_charge in quotation.taxes:
				desc_list = "{" + tax_charge.description + "}"
				args = frappe._dict(json.loads("{" + desc_list + "}"))
				if args.type == type and args.qty == applicable_charges[count-1]:
					# We finally found the correct charge for freight
					return tax_charge.price
		
	else:
		#Need to find the item price
		return 0