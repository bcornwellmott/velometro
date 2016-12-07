
from __future__ import unicode_literals

import frappe
from frappe import _, throw
from frappe.utils import flt

@frappe.whitelist()
def check_boms(bom_name):
	# This is where we check to see if the children of this bom have BOMs that are not the default
	
	bom = frappe.get_doc("BOM",bom_name)
	
	for item in bom.items:
		item_base = frappe.get_value("Item",item.item_code, "variant_of")
		
		if check_all_variants(item_base):
			frappe.msgprint(item.item_code+ " has unreleased versions.")
		if item.bom_no:
			status = frappe.get_value("BOM",item.bom_no, "is_default")
			
			if status != 1:
				frappe.msgprint(item.bom_no + " is out of date. Not checking children of this BOM")
			else:
				check_boms(item.bom_no)
		else:
			bom_no = frappe.get_value("Item",item.item_code, "default_bom")
			if bom_no != None and bom_no != "":
				frappe.msgprint(item.item_code+ " is missing its default BOM. Not checking children of this item.")
	frappe.msgprint("Finished checking BOMs")

@frappe.whitelist()
def check_all_variants(item_base):
	# This is where we find all variants of the part and make sure none are In Design (not Released or Obsolete)
	item_list = frappe.get_list('Item', fields=["name", "revision_status"], filters={'variant_of': item_base, 'disabled': 0})
	
	for my_item in item_list:
		if my_item.revision_status != "Released" and my_item.revision_status != "Obsolete":
			return 1
	return 0

@frappe.whitelist()			
def update_bom(bom_name):
	# This is where we try to update the boms to the default ones (for unsubmitted BOM

	bom = frappe.get_doc("BOM",bom_name)
	if bom.docstatus == 0:
		for item in bom.items:
			frappe.msgprint("Checking " + item.item_code)
			bom_no = frappe.get_value("Item",item.item_code, "default_bom")
			if bom_no == None:
				bom_no = ""
				
			if item.bom_no != bom_no:
				frappe.msgprint(item.item_code + " has a different BOM: " + bom_no)
				if not hasattr(bom, 'change_notice'):
					bom.change_notice = ""
				else:
					if bom.change_notice:
						bom.change_notice = bom.change_notice + "\n"
					else:
						bom.change_notice = ""
				if item.bom_no:
					bom.change_notice = bom.change_notice + bom_no + " WAS " + item.bom_no
				else: 
					bom.change_notice = bom.change_notice + bom_no + " ASSIGNED TO " + item.item_code
				item.bom_no = bom_no
				frappe.msgprint("Updated " + item.item_code)
				
		frappe.msgprint("Finished updating BOM")
		bom.save()
	else:
		frappe.msgprint("Can not update BOM after it is submitted")
		
				
