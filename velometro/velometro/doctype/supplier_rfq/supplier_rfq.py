# -*- coding: utf-8 -*-
# Copyright (c) 2015, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import get_files_path, cint
from frappe.utils.file_manager import get_file_path
from frappe.model.document import Document 
from frappe.model.mapper import get_mapped_doc
from frappe import _

class SupplierRFQ(Document): 

	def before_save(self):
		# Set the title based on the RFQ number and supplier code
		if not self.title:
			self.title = "-".join(filter(None, [self.rfq, self.supplier_code]))

	def validate(self):
		"""Ensure that the form has been filled out correctly"""

		# Make sure the rfq is set
		if not self.rfq:
			frappe.throw(_("The Request for Quotation must be selected"))

		# Make sure the supplier has been selected
		if not self.supplier:
			frappe.throw(_("The supplier must be selected"))

		# Make sure all the supplier info has been inputted
		rfqDoc = frappe.get_doc("Request for Quotation",self.rfq)
		for aSupplier in rfqDoc.suppliers:
			if aSupplier.supplier  == self.supplier:
				if not self.supplier_contact:
					self.supplier_contact = aSupplier.contact
				if not self.supplier_email:
					sContact = frappe.get_doc("Contact",aSupplier.contact)
					self.supplier_email = sContact.email_id
				if not self.supplier_code:
					supplier_doc = frappe.get_doc("Supplier",aSupplier.supplier)
					if supplier_doc.abbreviation:
						self.supplier_code = supplier_doc.abbreviation
					else:
						self.supplier_code = supplier_doc.supplier_name
			#else:
				#frappe.msgprint(_("{0} is not the same as {1}".format(aSupplier.supplier, self.supplier)))


		# Set the title based on the RFQ number and supplier code
		if not self.title:
			self.title = "-".join(filter(None, [self.rfq, self.supplier_code]))

		for i, item in enumerate(sorted(self.items, key=lambda item: item.item), start=1):
        		item.idx = i

		# Set the date 
		self.rfq_date = frappe.utils.nowdate()

	def on_submit(self):
		# Test sending the e-mail
		email_supplier(self) 


@frappe.whitelist()
def email_supplier(self):
	"""Sends an email to the supplier contact with the message"""
	
	my_attachments = [frappe.attach_print(self.doctype, self.name, file_name=self.name)]

	attachment_list = []
	for ref_item in self.items:
		my_attachments, attachment_list = get_attachments(ref_item,my_attachments, attachment_list) 

	frappe.sendmail(
		recipients=[self.supplier_email],
		subject=self.title,
		message=self.comments,
		reference_doctype=self.doctype,
		reference_name=self.name,
		attachments=my_attachments
		)
	frappe.msgprint(_("Sent E-Mail to Supplier"))


 
def get_attachments(rfq_item, attachments, attachment_list):
	"""Gets the attachments from each of the RFQ items as specified"""
	
	
	item = frappe.get_doc("Item",rfq_item.item)
	if rfq_item.include_pdf:
		filename = get_filename(item) + ".pdf"
		file = frappe.db.get_value("File", {"file_name": filename})
		if file == None:
			frappe.throw(_("{0} is not released to the Item. Make sure the drawing uploads match the revision number.").format(filename ))
		if not file in attachment_list:
			attachments.append(create_attachment(file))
			attachment_list.append(file)
	if rfq_item.include_stp:
		filename = get_filename(item) + ".stp"
		file = frappe.db.get_value("File", {"file_name": ["=", filename]})
		if file == None:
			frappe.throw(_("{0} is not released to the Item. Make sure the drawing uploads match the revision number and STP files were included in the release.").format(filename ))
		if not file in attachment_list:
			attachments.append(create_attachment(file))
			attachment_list.append(file)
	if rfq_item.include_dxf:
		filename = get_filename(item) + ".dxf"
		file = frappe.db.get_value("File", {"file_name": ["=", filename]})
		if file == None:
			frappe.throw(_("{0} is not released to the Item. Make sure the drawing uploads match the revision number and DXF files were included in the release.").format(filename ))
		if not file in attachment_list:
			attachments.append(create_attachment(file))
			attachment_list.append(file)
	if rfq_item.include_xt:
		filename = get_filename(item) + ".xt"
		file = frappe.db.get_value("File", {"file_name": ["=", filename]})
		if file == None:
			frappe.throw(_("{0} is not released to the Item. Make sure the drawing uploads match the revision number and Parasolid files were included in the release.").format(filename ))
		if not file in attachment_list:
			attachments.append(create_attachment(file))
			attachment_list.append(file)
	return attachments, attachment_list


def create_attachment(filename):
	"""Creates an attachment file for use with the sendmail attachments object"""
	file = frappe.get_doc("File",filename)
	path = get_file_path(file.file_name,)  
	frappe.msgprint(_("Adding file at {0} ".format(file.file_name)))

	with open(path, "rb") as fileobj:
		filedata = fileobj.read() 

	out = {
		"fname": file.file_name,
		"fcontent": filedata
	}
	return out 

@frappe.whitelist() 
def get_filename(item):
	"""Gets the file name based on the project code, item number and revision level of the item"""
	
	filename = item.project + "-" + item.item_code + "_R" + item.revision + " " + item.description

	return filename

def set_missing_values(source, target_doc):
	target_doc.run_method("set_missing_values")
	target_doc.run_method("calculate_taxes_and_totals")


@frappe.whitelist() 
def create_supplier_quotation(source_name, target_doc = None):
	"""Generates a Supplier Quotation based on this Supplier RFQ form"""

		
	def postprocess(source,target):
		# Set the supplier information
		target.ignore_pricing_rule = 1
		set_missing_values(source,target)
		target.buying_price_list = source.supplier
		
	def process_item(obj, target, source_parent):
		target.item_code = obj.item
		target.rate = 0
		target.price_list_rate = 0
		frappe.msgprint("parent {0}".format(target.parent))
		frappe.msgprint("parenttype {0}".format(target.parenttype))
		frappe.msgprint("name {0}".format(target.name))


	#supplier_rfq =  frappe.get_doc("Supplier RFQ",source_name)  

	#if target_doc.doctype == "Supplier Quotation": 
		 
	doc= get_mapped_doc("Supplier RFQ", source_name,{
		"Supplier RFQ": { 
			"doctype": "Supplier Quotation", 
			"field_map": {
				"supplier": "supplier" 			
			}
			
		},
		"RFQ Item": {
			"doctype": "Supplier Quotation Item",
			"field_map": {
				"qty": "qty" 
			},
			"postprocess": process_item 
		}}, target_doc,postprocess) 
	

	#else: 
	#	frappe.throw(_("Create Supplier Quotation was passed the wrong doctype"))
	
	return doc 


	
 