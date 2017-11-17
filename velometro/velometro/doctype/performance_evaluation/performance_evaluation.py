# -*- coding: utf-8 -*-
# Copyright (c) 2017, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class PerformanceEvaluation(Document):
	
	def validate(self):
		self.validate_date()
		self.validate_employee()
		
	def validate_date(self):
		if not self.review_date:
			self.review_date = frappe.utils.nowdate()
			
	def validate_employee(self):
		# Check to see if there are any reviews for this employee
		active_reviews = frappe.db.sql("""SELECT pe.name as name
			FROM `tabPerformance Evaluation` AS pe
			WHERE pe.review_status = 0
				AND pe.target_employee = %(target)s
				AND pe.employee = %(employee)s
				AND pe.docstatus < 1
			ORDER BY
				pe.review_date""", {"employee": self.employee, "target": self.target_employee}, as_dict=1)
		if active_reviews:
			if len(active_reviews) > 0 and active_reviews[0].name != self.name:
				frappe.throw(_("You cannot submit more than one evaluation for an employee in a week"))
		
	
