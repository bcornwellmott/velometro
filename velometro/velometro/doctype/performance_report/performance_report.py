# -*- coding: utf-8 -*-
# Copyright (c) 2017, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.core.doctype.communication.email import make

STANDARD_USERS = ("Guest", "Administrator")

class PerformanceReport(Document):

	def validate(self):
		self.validate_names()
		
	def validate_names(self):
		self.employee_name = frappe.get_value("Employee", self.employee, "employee_name")
		self.manager_name = frappe.get_value("Employee", self.manager, "employee_name")
		
		
	def email_report_to_manager(self):

		args = {
			'report_link': self.get_url(),
			'employee': self.employee
		}

		subject = _("Performance Evaulation: " + self.employee)
		template = "templates/emails/performance_report.html"
		sender = frappe.session.user not in STANDARD_USERS and frappe.session.user or None
		message = frappe.get_template(template).render(args)

		self.send_email(self.manager_email, sender, subject, message)

		
	def send_email(self, email, sender, subject, message):
		#make(subject = subject, content=message,recipients=email,
		#	sender=sender, send_email=True,
		#     	doctype=self.doctype, name=self.name)["name"]

		frappe.msgprint(_("Email sent to manager {0}").format(self.manager_name))
		
		
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
		my_doc.manager_email = frappe.get_value("Employee", my_doc.manager,"user_id")
		my_doc.email = frappe.get_value("Employee", employee,"user_id")
		for review in active_reviews:
			entry = frappe.get_doc({
				"doctype": "Performance Report Review",
				"eval": review.name,
				"review_date": review.review_date,
				"reviewing_employee": review.employee,
				"rating": review.rating,
				"comments": review.comments
				})
			my_doc.append('reviews',entry)
			#frappe.set_value("Performance Evaluation", review.name, "review_status", 1)
		my_doc.update()
		my_doc.email_report_to_manager()

@frappe.whitelist()
def make_performance_meeting(performance_report):
	report = frappe.get_doc("Performance Report", performance_report)

	meeting = frappe.new_doc("Performance Meeting")
	meeting.report = performance_report
	employee = frappe.get_doc({
				"doctype": "Performance Meeting Attendee",
				"employee": report.employee,
				"employee_name": report.employee_name
				})
	manager = frappe.get_doc({
				"doctype": "Performance Meeting Attendee",
				"employee": report.manager,
				"employee_name": report.manager_name
				})
	meeting.append('attendees',employee)
	meeting.append('attendees',manager)
	meeting.save()
	return meeting.as_dict()
		
				
