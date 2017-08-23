import frappe
from frappe.utils import cint

def execute():
	frappe.reload_doc('stock', 'doctype', 'Item')
	for item in frappe.get_all('Item', fields=["*"],	filters=[]):
		item.notes = item.description
		item.save()
