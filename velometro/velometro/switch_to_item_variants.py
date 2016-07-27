import frappe
import erpnext

from frappe.utils import cint, cstr
from erpnext.controllers.item_variant import (create_variant, copy_attributes_to_variant,
	make_variant_item_code, validate_item_variant_attributes, ItemVariantExistsError)
	
def execute():
	i = 1
	for item in frappe.get_all('Item', fields=["name"],	filters=[]):
		item_doc = frappe.get_doc('Item',item.name)
		print "\nLooping for: " + item_doc.name
		if item_doc.has_variants != 1:
			item_doc.has_variants = 1
			if not item_doc.attributes:
				item_doc.append('attributes',get_attribute(item_doc.name, item_doc.revision))
			item_doc.save()
		args = {"Revision": cstr(item_doc.revision)}

		new_variant = create_variant(item_doc.name, args)
		new_variant.item_code = item_doc.name + "_" + cstr(item_doc.revision)
		new_variant.item_name = item_doc.item_name
		
		
		print new_variant.item_name
		new_variant.insert()
		
		i = i + 1
		#if i > 1:
			#return

def get_attribute(item, rev):
	return {"modified_by":"Administrator",
			"parent":item,
			"numeric_values":0,
			"attribute":"Revision",
			"attribute_value":rev,
			"to_range":1000,
			"idx":1,
			"parenttype":"Item",
			"increment":1,
			"owner":"Administrator",
			"docstatus":0,
			"doctype":"Item Variant Attribute",
			"from_range":0.0,
			"parentfield":"attributes"}