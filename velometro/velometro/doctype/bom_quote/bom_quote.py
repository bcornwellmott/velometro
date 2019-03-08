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
			quote_details = find_cheapest_price(purchased, purchased.qty_per_asm  * self.quantity)
			
			purchased.qty = purchased.qty_per_asm  * self.quantity
			if quote_details is not None:
				purchased.purchase_rate = quote_details.rate
				purchased.supplier_quotation_link = quote_details.supplier_quotation_parent
				purchased.revision = quote_details.revision
				purchased.total_price = quote_details.rate * purchased.qty
				unit_pcost += purchased.qty_per_asm  * purchased.purchase_rate

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
		
		# Merge duplicates
		i = 0
		while i < (len(self.items) - 1):
			if self.items[i].item == self.items[i+1].item:
				self.items[i].qty_per_asm += self.items[i+1].qty_per_asm
				del self.items[i+1]
			else:
				i+=1
			
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
		item_quantity = qty * myItem.stock_qty  
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
	doc.description = frappe.get_value("Item",doc.item,"description")
	doc.stock_uom = frappe.get_value("Item",doc.item,"stock_uom")
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

	
def find_cheapest_price(item, qty):
	"""Goes through all the supplier quotations to find the cheapest price with a quantity less than the indicated quantity"""
	
	
	base_doc = frappe.get_doc("Item", item.item)
	quote_details = find_version_pricing(item.item, qty, base_doc.revision)
	
	if quote_details.rate < 0:
		# We need to see if there are previous versions that have been quoted
		parent_doc = frappe.get_value("Item", item.item, "variant_of")
		versions = frappe.get_all('Item',filters={'variant_of': parent_doc}, fields=['item_code', 'revision'], order_by='revision desc')
		
		for version in versions:
			quote_details = find_version_pricing(version.item_code, qty, version.revision)
			if quote_details.rate > 0:
				
				#frappe.msgprint("Found OLD rate of {0}for {1} from {2}".format(quote_details.rate, item.item, quote_details.supplier_quotation_parent))
				return quote_details
	else: 
		#frappe.msgprint("Found CORRECT rate of {0}for {1} from {2}".format(quote_details.rate, item.item, quote_details.supplier_quotation_parent))
		return quote_details
	return None
				
			
def find_version_pricing(item, qty, revision):
	quote_details = {
		"rate": -1,
		"supplier_quotation_parent":"",
		"revision": revision
		}
		
	quote_details = frappe._dict(quote_details) 
	quotes = frappe.get_all('Supplier Quotation Item',filters={'item_code': item, 'docstatus':1}, fields=['name', 'qty', 'base_rate', 'conversion_factor', 'parent'])
	for quote in quotes: 
		if quote.qty <= qty:
			suom_rate = quote.base_rate / quote.conversion_factor
			# We have a valid quote
			if(quote_details.rate < 0 or (quote_details.rate > 0 and suom_rate > 0 and suom_rate < quote_details.rate)):
			
				#frappe.msgprint("Found rate of {0} for {1} from {2}".format(suom_rate,item,  quote.name ))
				quote_details.supplier_quotation_parent = quote.parent
				quote_details.rate = suom_rate
		
	return quote_details
	