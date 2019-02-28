from __future__ import unicode_literals

import frappe

def get_context(context):
	# do your magic here
	context.my_context = context
	
	context.employee = frappe.db.sql("""select name
		from `tabEmployee`
		where user_id = %(user)s""", {"user": frappe.session.user})[0][0]
			
	context.employee_names = frappe.db.sql("""select name, employee_name from `tabEmployee`
		where status = 'Active'
			and docstatus < 2
		order by
			name, employee_name""")
			
	context.active_reviews = frappe.db.sql("""select pe.name, emp.employee_name, pe.rating, pe.comment 
		from `tabPerformance Evaluation` as pe
		join `tabEmployee` as emp
		where pe.review_status = 0
			and emp.name = pe.target_employee
			and pe.docstatus < 1
		order by
			pe.review_date""", {"employee": context.employee})
			
	
	pass

	
