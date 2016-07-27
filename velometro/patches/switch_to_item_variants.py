import frappe
from frappe.utils import cint

def execute():
	for item in frappe.get_all('Item', fields=["*"],	filters=[]):
		item.has_variants = 1
		item.save()
