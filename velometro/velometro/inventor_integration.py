
from __future__ import unicode_literals

import frappe
from frappe import _, throw
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item, get_pricing_rules, filter_pricing_rules, apply_pricing_rule
from frappe.utils import flt

@frappe.whitelist()
def get_item_revision_list(item_code):
	item_list = {}
	for d in frappe.db.sql("""select item_code, revision
					from `tabItem`
					where variant_of = %(item_base)s""", {"item_base":item_code}, as_dict=1):
						item_list.append(d.revision, d.item_code)
	
	return item_list
	
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
	frappe.msgprint("Running")
	for d in frappe.db.sql("""select bom.name from `tabBOM` bom, `tabBOM Item` fbi, `tabItem` item where bom.name = fbi.parent and bom.is_active = 1 and fbi.item_code = item.item_code and  item.variant_of  = %(item_code)s""",{"item_code":item_code}, as_dict=1):
		frappe.msgprint("Got in the loop")
		bom_list.append(d.name)
	return bom_list
	
@frappe.whitelist()
def get_affected_parent_boms(bom_no):
	bom_list = []
	for d in frappe.db.sql("""select distinct bom.name from `tabBOM` bom, `tabBOM Item` fbi where bom.name = fbi.parent and bom.is_active = 1 and fbi.bom_no = %(bom_no)s""",{"bom_no":bom_no}, as_dict=1):
		bom_list.append(d.name)
		for level_up in get_affected_parent_boms(d.name):
			if level_up not in bom_list:
				bom_list.append(level_up)
	return bom_list