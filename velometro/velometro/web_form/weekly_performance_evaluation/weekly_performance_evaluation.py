from __future__ import unicode_literals

import frappe

def get_context(context):
	user = frappe.get_value("User", {"email": frappe.session.user}, "name")
	frappe.form_dict.employee = user
