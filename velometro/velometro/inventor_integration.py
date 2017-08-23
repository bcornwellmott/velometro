
from __future__ import unicode_literals

import frappe
from frappe import _, throw
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item, get_pricing_rules, filter_pricing_rules, apply_pricing_rule
from frappe.utils import flt
from frappe.desk.tags import DocTags

@frappe.whitelist()
def get_item_revision_list(item_code):
	item_list = {}
	for d in frappe.db.sql("""select item_code, revision
					from `tabItem`
					where variant_of = %(item_base)s""", {"item_base":item_code}, as_dict=1):
						item_list.append(d.revision, d.item_code)
	
	return item_list
	

@frappe.whitelist()
def add_tag(dt,dn,tag): 
	DocTags(dt).add(dn,tag)			
	return tag
	
@frappe.whitelist()
def remove_tag(dt,dn,tag): 
	DocTags(dt).remove(dn,tag)		
	return tag

@frappe.whitelist()
def update_tags(dt,dn,tags):
	tl = tags.split(',')
	DocTags(dt).update(dn,tl)
	

@frappe.whitelist(allow_guest=True)
def get_item_tags(): 
	item_list = []
	for d in frappe.db.sql("""select _user_tags	from `tabItem` where not isnull(_user_tags)""",{}, as_dict=1):
		mylist = d._user_tags.split(",")
		for q in mylist:
			if q not in item_list:
				item_list.append(q)
	for d in frappe.db.sql("""select _user_tags	from `tabSupplier` where not isnull(_user_tags)""",{}, as_dict=1):
		mylist = d._user_tags.split(",")
		for q in mylist:
			if q not in item_list:
				item_list.append(q)
				
	return ",".join(item_list)

@frappe.whitelist(allow_guest=True)
def get_tool_tags(): 
	item_list = []
	for d in frappe.db.sql("""select _user_tags	from `tabBOM` where not isnull(_user_tags)""",{}, as_dict=1):
		mylist = d._user_tags.split(",")
		for q in mylist:
			if q not in item_list:
				item_list.append(q)

	return ",".join(item_list)
	
@frappe.whitelist()
def get_affected_boms(item_code):
	bom_list = []
	for d in frappe.db.sql("""select bom.name from `tabBOM` bom, `tabBOM Item` fbi, `tabItem` item where bom.name = fbi.parent and bom.is_default = 1 and fbi.item_code = item.item_code and  item.variant_of  = %(item_code)s""",{"item_code":item_code}, as_dict=1):
		bom_list.append(d.name)
	return bom_list
	
@frappe.whitelist()
def get_affected_parent_boms(bom_no):
	bom_list = []
	for d in frappe.db.sql("""select distinct bom.name from `tabBOM` bom, `tabBOM Item` fbi where bom.name = fbi.parent and bom.is_default = 1 and fbi.bom_no = %(bom_no)s""",{"bom_no":bom_no}, as_dict=1):
		bom_list.append(d.name)
		#for level_up in get_affected_parent_boms(d.name):
		#if level_up not in bom_list:
		#bom_list.append(level_up)
	return bom_list
	
def update_description(doc, method):
	mfg = "OEM"
	notes = ""
	if doc.get("notes") != None:
		notes = doc.get("notes")
	if doc.get("manufacturer") != None:
		mfg = frappe.get_value("Manufacturer", doc.get("manufacturer"), "short_name")
	if doc.get("manufacturer_part_no") != None:
		description = str(notes) + " (" + str(mfg) + " PN: " + str(doc.get("manufacturer_part_no")) + ")"
	else:
		description = str(notes)
	doc.set("description", description)
	
