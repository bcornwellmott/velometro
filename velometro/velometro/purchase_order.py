
from __future__ import unicode_literals

import frappe
from frappe import _, throw
from frappe.utils import flt
from frappe.utils.file_manager import save_url
import json


@frappe.whitelist()
def attach_all_docs(document, method=None):
	"""This function attaches drawings to the purchase order based on the items being ordered"""
	document = json.loads(document)
	
	current_attachments = []
	for file_url in frappe.db.sql("""select file_url from `tabFile` where attached_to_doctype = %(doctype)s and attached_to_name = %(docname)s""", {'doctype': document["doctype"], 'docname': document["name"]}, as_dict=True ):
		current_attachments.append(file_url.file_url)
	count = 0
	for item_doc in document["items"]:
		#frappe.msgprint(item_doc)
		# Check to see if the quantity is = 1
		item = frappe.get_doc("Item",item_doc["item_code"])
		
		attachments = []
		# Get the path for the attachments
		if item.drawing_attachment:
			attachments.append(item.drawing_attachment)
		if item.stp_attachment:
			attachments.append(item.stp_attachment)
		if item.dxf_attachment:
			attachments.append(item.dxf_attachment)
		if item.x_t_attachment:
			attachments.append(item.x_t_attachment)
			
		for attach in attachments:
			# Check to see if this file is attached to the one we are looking for
			if not attach in current_attachments:
				count = count + 1
				save_url(attach, document["doctype"], document["name"], "Home/Attachments")
	frappe.msgprint("Attached {0} files".format(count))
		
				 


