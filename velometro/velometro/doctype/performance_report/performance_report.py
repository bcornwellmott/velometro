# -*- coding: utf-8 -*-
# Copyright (c) 2017, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PerformanceReport(Document):
	pass

@frappe.whitelist()
def generate_reports():
	employee_names = frappe.db.sql("""select name, employee_name from `tabEmployee`
		where status = 'Active'
			and docstatus < 2
		order by
			name, employee_name""", as_dict=1)
	
	for emp in employee_names:
		generate_report(emp.name)
			
def generate_report(employee):
	#Get a list of all the reports for a given employee
	active_reviews = frappe.db.sql("""SELECT pe.name AS name, 
			pe.employee AS employee, 
			pe.comment AS comments, 
			pe.review_date AS review_date, 
			pe.rating AS rating
		FROM `tabPerformance Evaluation` AS pe
		WHERE pe.review_status = 0
			AND pe.target_employee = %(target)s
			AND pe.docstatus < 1
		ORDER BY
			pe.review_date""", {"target": employee}, as_dict=1)
	if active_reviews:
		my_doc = frappe.new_doc("Performance Report")
		my_doc.employee = employee
		my_doc.report_date = frappe.utils.nowdate()
		my_doc.manager = frappe.get_value("Employee", employee,"reports_to")
		my_doc.email = frappe.get_value("Employee", employee,"user_id")
		for review in active_reviews:
			entry = frappe.get_doc({
				"doctype": "Performance Report Review",
				"review_date": review.review_date,
				"reviewing_employee": review.employee,
				"rating": review.rating,
				"comments": review.comments
				})
			my_doc.append('reviews',entry)
			#frappe.set_value("Performance Evaluation", review.name, "review_status", 1)
		my_doc.save()
				