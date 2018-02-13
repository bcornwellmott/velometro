from __future__ import unicode_literals

import frappe
from frappe import _, throw, ValidationError
from frappe.utils import getdate
import json

class InvalidVacationHoursError(frappe.ValidationError): pass


@frappe.whitelist()
def check_for_new_leave(self, method):
	"""Verifies each timesheet detail and identifies a list of vacation requests without leave applications created"""
	#doc = frappe.get_doc("Timesheet", self)

	#new_leaves = []
	for detail in self.time_logs:
		is_overlap = 0
		if detail.activity_type == "VMI091 - Vacation":
			# Make sure a multiple of 4 hours
			if detail.hours % 4 != 0:
				frappe.throw(_('Vacation requests must be made for 4 hrs or 8 hours'), InvalidVacationHoursError)
		 	#Check to make sure there is no leave application for the employee for these dates
			for d in frappe.db.sql("""
				select name
				from `tabLeave Application`
				where employee = %(employee)s and docstatus < 2 and status in ("Open", "Approved")
				and leave_type = %(activity)s
				and to_date >= %(from_time)s and from_date <= %(to_time)s""", {
					"employee": self.employee,
					"from_time": getdate(detail.from_time),
					"to_time": getdate(detail.to_time),
					"activity": "Vacation"
				}, as_dict = 1):
				is_overlap = 1
				frappe.msgprint("Linking vacation between " + str(getdate(detail.from_time)) + " and " + str(getdate(detail.to_time)) + " to Leave Application " + d.name)
				detail.leave_application = d.name
				
			if not is_overlap:
				#new_leaves.append(detail)
				#frappe.msgprint("Vacation Leave Application needs to be created for " + detail.from_time)
				link = create_leave(detail, self.employee, 'Vacation')
				detail.leave_application = link
				detail.save()
				
		elif detail.activity_type == "VMI095 - Holiday Shutdown":
			if detail.hours % 4 != 0:
				frappe.throw(_('Vacation requests must be made for 4 hrs or 8 hours'), InvalidVacationHoursError)
			for d in frappe.db.sql("""
				select name
				from `tabLeave Application`
				where employee = %(employee)s and docstatus < 2 and status in ("Open", "Approved")
				and leave_type = %(activity)s
				and to_date >= %(from_time)s and from_date <= %(to_time)s""", {
					"employee": self.employee,
					"from_time": getdate(detail.from_time),
					"to_time": getdate(detail.to_time),
					"activity": "Holiday Shutdown"
				}, as_dict = 1):
				is_overlap = 1
				frappe.msgprint("Linking vacation between " + str(getdate(detail.from_time)) + " and " + str(getdate(detail.to_time)) + " to Leave Application " + d.name)
				detail.leave_application = d.name
				
			if not is_overlap:
				#new_leaves.append(detail)
				#frappe.msgprint("Vacation Leave Application needs to be created for " + detail.from_time)
				link = create_leave(detail, self.employee,'Holiday Shutdown')
				detail.leave_application = link
				detail.save()
	frappe.clear_cache()
	
def create_leave(detail, employee, type):

	emp = frappe.get_doc("Employee", employee)
	approvers = [l.leave_approver for l in emp.get("leave_approvers")]
	mydict = dict(doctype='Leave Application', 
		naming_series='LAP/', 
		leave_type=type, 
		status='Open', 
		from_date=getdate(detail.from_time), 
		to_date=getdate(detail.to_time), 
		leave_approver = approvers[0],
		employee=employee,
		total_leave_days=detail.hours/8.0)
	if detail.hours == 4:
		mydict['half_day'] = 1
	my_leave = frappe.get_doc(mydict).insert()
	frappe.msgprint("Created Leave Application for " + type + " on " + str(getdate(detail.from_time)) + ". Please make sure you submit this Leave Application to your Leave Approver.")
	return my_leave.name
