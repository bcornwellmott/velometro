from __future__ import unicode_literals

import frappe
import os, base64
from frappe import _, throw
from frappe.utils import flt
from frappe.utils.file_manager import save_url, save_file, get_file_name, remove_all, remove_file
from frappe.utils import get_site_path, get_files_path, random_string, encode
import json


@frappe.whitelist()
def remove_all_docs(document):
	"""This function attaches drawings to the purchase order based on the items being ordered"""
	document = json.loads(document)
	document2 = frappe._dict(document)
	
	remove_all(document2.doctype, document2.name)

@frappe.whitelist()
def remove_non_zip_docs(document):
	"""This function attaches drawings to the purchase order based on the items being ordered"""
	document = json.loads(document)
	document2 = frappe._dict(document)
	
	current_attachments = []
	
	for file_url in frappe.db.sql("""select name, file_url from `tabFile` where attached_to_doctype = %(doctype)s and attached_to_name = %(docname)s""", {'doctype': document2.doctype, 'docname': document2.name}, as_dict=True ):
		if not file_url.file_url.endswith(".zip"):
			remove_file(file_url.name, document2.doctype, document2.name)

@frappe.whitelist()
def attach_all_docs(document):
	"""This function attaches drawings to the purchase order based on the items being ordered"""
	document = json.loads(document)
	document2 = frappe._dict(document)
	
	current_attachments = []
	
	for file_url in frappe.db.sql("""select file_url from `tabFile` where attached_to_doctype = %(doctype)s and attached_to_name = %(docname)s""", {'doctype': document2.doctype, 'docname': document2.name}, as_dict=True ):
		current_attachments.append(file_url.file_url)
	
	# add the directly linked drawings
	items = []
	for item in document["items"]:
		#frappe.msgprint(str(item))
		items.append(item["item_code"])
		
		#add the child documents (from boms)
		items = add_bom_items(items, item["item_code"])
	
	
	count = 0
	for item_doc in items:
		#frappe.msgprint(item_doc)
		item = frappe.get_doc("Item",item_doc)
		
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
		if item.electrical_attachment:
			attachments.append(item.electrical_attachment)
			
		for attach in attachments:
			# Check to see if this file is attached to the one we are looking for
			if not attach in current_attachments:
				count = count + 1
				myFile = save_url(attach, attach, document2.doctype, document2.name, "Home/Attachments",1)
				myFile.file_name = attach
				myFile.save()
				current_attachments.append(attach)
				
	frappe.msgprint("Attached {0} files".format(count))

@frappe.whitelist()
def attach_all_boms(document):
	"""This function attaches drawings to the purchase order based on the items being ordered"""
	document = json.loads(document)
	document2 = frappe._dict(document)
	
	current_attachments = []
	
	for file_url in frappe.db.sql("""select file_name from `tabFile` where attached_to_doctype = %(doctype)s and attached_to_name = %(docname)s""", {'doctype': document2.doctype, 'docname': document2.name}, as_dict=True ):
		current_attachments.append(file_url.file_name)
	
	# add the directly linked drawings
	boms = []
	for item in document["items"]:
		#add the boms
		boms = get_bom_pdf(boms, item["item_code"])
	
	count = 0
	for bom_doc in boms:
		#frappe.msgprint(item_doc)
		bom = frappe.get_doc("BOM",bom_doc)
		
		# Check to see if this file is attached to the one we are looking for
		if not (bom.name + ".pdf") in current_attachments:
			count = count + 1
			my_attach = frappe.attach_print(bom.doctype, bom.name, doc=bom)
			myFile = save_file(my_attach['fname'], my_attach['fcontent'], document2.doctype, document2.name, "Home/Attachments",False,1)
			myFile.file_name = my_attach['fname']
			myFile.save()
			current_attachments.append(my_attach['fname'])
				
	frappe.msgprint("Attached {0} boms".format(count))
	
def get_bom_pdf(boms, item_code):	
	bom_num = frappe.get_value("Item",item_code, "default_bom")
	if bom_num:
		boms.append(bom_num)
		bom = frappe.get_doc("BOM",bom_num)
		for bom_item in bom.items:
			boms = get_bom_pdf(boms, bom_item.item_code)
	return boms

	
def add_bom_items(items, item_code):
	bom_num = frappe.get_value("Item",item_code, "default_bom")
	if bom_num:
		bom = frappe.get_doc("BOM",bom_num)
		for bom_item in bom.items:
			items.append(bom_item.item_code)
			items = add_bom_items(items, bom_item.item_code)
	return items

@frappe.whitelist()	
def zip_attachments(document):
	zip_count = 1
	zip_size = 0
	document = json.loads(document)
	document2 = frappe._dict(document)

	
	fname = get_file_name(document2.name + " (zip 1).zip", random_string(7))
	
	import zipfile
	docZip = zipfile.ZipFile(fname,"w", zipfile.ZIP_DEFLATED)
	
	
	for file_url in frappe.db.sql("""select file_url, is_private from `tabFile` where attached_to_doctype = %(doctype)s and attached_to_name = %(docname)s""", {'doctype': document2.doctype, 'docname': document2.name}, as_dict=True ):
		frappe.msgprint("Adding " + file_url.file_url)
		
		if file_url.file_url.startswith("/private/files/"):
			path = get_files_path(*file_url.file_url.split("/private/files/", 1)[1].split("/"), is_private=1)

		elif file_url.file_url.startswith("/files/"):
			path = get_files_path(*file_url.file_url.split("/files/", 1)[1].split("/"))
		
		path = encode(path)
		if zip_size + os.path.getsize(path) > 10000000:
			zip_count = zip_count + 1
			zip_size = 0
			docZip.close()
			with open(encode(fname), 'r') as f:
				content = f.read()
			
			content = base64.b64encode(content)
				
			save_file(fname, content, document2.doctype, document2.name, "Home/Attachments", 1)
			fname = get_file_name(document2.name + " (zip " + str(zip_count) + ").zip", random_string(7))
			docZip = zipfile.ZipFile(fname,"w", zipfile.ZIP_DEFLATED)
		docZip.write(path, os.path.basename(path))
		zip_size  = zip_size + docZip.getinfo(os.path.basename(path)).compress_size
		

	docZip.close()
	with open(encode(fname), 'r') as f:
		content = f.read()
	
	content = base64.b64encode(content)
		
	save_file(fname, content, document2.doctype, document2.name, "Home/Attachments", 1)
