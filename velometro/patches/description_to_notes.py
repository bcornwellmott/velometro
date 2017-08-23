import frappe
from frappe.utils import cint

def execute():
	frappe.reload_doc('stock', 'doctype', 'item')
	for d in frappe.get_all('Item', fields=["name"], filters=[]):
		item = frappe.get_doc("Item", d.name)
		item.notes = item.description
		item.save()
