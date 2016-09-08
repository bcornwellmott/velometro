import frappe
from frappe.utils import cint

def execute():
	frappe.db.sql("""update `tabItem` set default_supplier = '' where default_supplier != '' """)

