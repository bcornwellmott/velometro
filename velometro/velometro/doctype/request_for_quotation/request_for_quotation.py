# -*- coding: utf-8 -*-
# Copyright (c) 2015, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils.file_manager import get_file_path
from frappe import _
from velometro.velometro.doctype.supplier_rfq.supplier_rfq import get_filename
import os.path

class RequestforQuotation(Document):
	
	def validate(self):
		"""Ensure that all the values can get updated"""


		# Make sure the company name is set
		cpny = frappe.get_doc("Company",self.company)
		if not self.company_address:
			self.company_address = cpny.address
		
		# Make sure all the items have their quantities filled in, the descriptions are filled out, and the supplier part number is blank
		for item in self.items:
			set_item_details(item)

		# Make sure each of the suppliers have contact information
		for supplier in self.suppliers:
			verify_supplier_contact(supplier)

	def on_submit(self):
		for supplier in self.suppliers:
			make_supplier_RFQ(self.name,supplier)
 
		 
			
@frappe.whitelist()		
def set_item_details(item):
	item_doc = frappe.get_doc("Item", item.item)
	if not item.description:
		item.description = item_doc.description
	if item.supplier_code:
		item.supplier_code = ""
	if not item.qty:
		# Throw an error when you find out how
		frappe.throw(_("Item {0} cannot have 0 quantity").format(item.item))
	if not item.revision:
		item.revision = item_doc.revision

@frappe.whitelist() 
def get_item_attachments(item_code):
	item_doc = frappe.get_doc("Item", item_code)
	
	test = check_file_exists(item_doc,".pdf")
	if test:
		include_pdf = True
	else:
		#frappe.msgprint(_("Cannot find pdf"))
		include_pdf = False

	test = check_file_exists(item_doc,".xt")
	if test:
		include_xt = True
	else:
		#frappe.msgprint(_("Cannot find xt"))
		include_xt = False

	test = check_file_exists(item_doc,".stp")
	if test:
		include_stp = True 
	else:
		#frappe.msgprint(_("Cannot find stp"))
		include_stp = False


	test = check_file_exists(item_doc,".dxf")
	if test: 
		include_dxf = True 
	else:
		#frappe.msgprint(_("Cannot find dxf"))
		include_dxf = False

	message = {
			"include_pdf": include_pdf,
			"include_dxf": include_dxf,
			"include_xt": include_xt,
			"include_stp": include_stp
	}
	return message

def check_file_exists(item, extension):
	name = get_file_path(get_filename(item) + extension)
	frappe.msgprint(name)
	return os.path.isfile(name)
	
  
 
@frappe.whitelist()		
def verify_supplier_contact(supplier):

	if not supplier.contact:
		frappe.throw(_("Supplier {0} must have a valid contact").format(supplier.supplier))

@frappe.whitelist()
def make_supplier_RFQ(self, supplier):
	"""Generates a supplier RFQ for the designated supplier based on this RFQ form"""

	def update_item(obj, target, source_parent):
		# Set the supplier code
		supplier_doc = frappe.get_doc("Supplier",supplier.supplier)
		target.supplier_code = ""
		target.include_pdf = obj.include_pdf
		target.include_stp = obj.include_stp
		target.include_xt = obj.include_xt
		target.include_dxf = obj.include_dxf 

		# Duplicate the item for each vehicle quantity
		target.qty = obj.qty * qties.qty
		
		
	def postprocess(source,target):
		# Set the supplier information
		supplier_doc = frappe.get_doc("Supplier",supplier.supplier)
		target.supplier = supplier_doc.supplier_name
		if supplier_doc.abbreviation:
			target.supplier_code = supplier_doc.abbreviation
		else:
			target.supplier_code = supplier_doc.supplier_name


		target.title = "-".join(filter(None, [source.name, target.supplier_code]))
		target.comments = "\n".join(filter(None,[source.message,supplier.notes])) 
 
	doc = frappe.get_doc({"doctype":"Supplier RFQ", "title":"test"})

	rfq_doc = frappe.get_doc("Request for Quotation",self) 

	for qties in rfq_doc.quantities:
		doc = get_mapped_doc("Request for Quotation", self,	{
			"Request for Quotation": {
				"doctype": "Supplier RFQ"
				
			},
			"RFQ Item": {
				"doctype": "RFQ Item",
				"field_map": {
					"name": "prevdoc_detail_docname",
					"parent": "prevdoc_docname",
					"parenttype": "prevdoc_doctype",
					"include_pdf": "include_pdf",
					"include_stp": "include_stp",
					"include_xt": "include_xt", 
					"include_dxf": "include_dxf" 
				},
				"postprocess": update_item
			}}, doc,postprocess)
		
	

	
	
	doc.insert(ignore_permissions = True)
	frappe.msgprint("Created new doc")
	
