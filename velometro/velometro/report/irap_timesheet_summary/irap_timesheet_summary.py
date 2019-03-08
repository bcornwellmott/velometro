# Copyright (c) 2019, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import openpyxl
from frappe.utils import date_diff, cstr
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee


def execute(filters=None):
	columns, data = [], []
	if filters.start_date and filters.end_date:
		columns = get_columns(filters.start_date, filters.end_date)
		data = get_hours(columns, filters.start_date, filters.end_date)

	return columns, data

def get_hours(columns, start_date, end_date):
	out = []
	
	# set up data for last column
	ytd_total = 0
	
	activities = []
	i = 0
	for i in range(2,len(columns)-1):
		activities.append(columns[i]['label'])
	
	# Do each employee
	for employee in frappe.db.sql("""SELECT 
			sheet.employee,
			sheet.employee_name
		FROM `tabTimesheet Detail` as detail, `tabTimesheet` as sheet 
		WHERE detail.from_time BETWEEN %(start_time)s AND %(end_time)s AND
			detail.parent = sheet.name AND
			sheet.docstatus = 1
		GROUP BY employee 
		ORDER BY employee ASC""", {"end_time": end_date, "start_time":start_date}, as_dict=1):
		
		total_hrs = 0
		ot_hrs = 0
		times = [0] * len(activities)
		
		for timesheet_hrs in frappe.db.sql("""SELECT SUM(detail.hours) as hours, detail.activity_type as type 
			FROM `tabTimesheet Detail` as detail, `tabTimesheet` as sheet 
			WHERE cast(detail.from_time as date) BETWEEN %(start_time)s AND %(end_time)s AND 
				detail.parent = sheet.name AND 
				sheet.docstatus = 1 AND 
				sheet.employee = %(employee)s
			GROUP BY type 
			ORDER BY type ASC""", {"employee": employee.employee, "start_time":start_date, "end_time": end_date}, as_dict=1):
			total_hrs += timesheet_hrs.hours
			times[activities.index(timesheet_hrs.type)] += timesheet_hrs.hours
		temp = {
				"employee": employee.employee,
				"emp_name": employee.employee_name,
				"total_hours": total_hrs,
				"overtime_hours": ot_hrs
			}
		for i in range(len(activities)):
			temp['activity_'+cstr(i)] = times[i]
			
		out.append(frappe._dict(temp))
		
	
	return out
	
	

def get_columns(start_date, end_date):
	columns = [{
		"fieldname": "employee",
		"label": "Employee Number",
		"fieldtype": "Data",
		"options": "",
		"width": 120
	}, {
		"fieldname": "emp_name",
		"label": "Employee Name",
		"fieldtype": "Data",
		"options": "",
		"width": 120
	}]
	
	i = 0
	for activity in frappe.db.sql("""SELECT 
			detail.activity_type as activity_type 
		FROM `tabTimesheet Detail` as detail, `tabTimesheet` as sheet 
		WHERE detail.from_time BETWEEN %(start_time)s AND %(end_time)s AND
			detail.parent = sheet.name AND
			sheet.docstatus = 1
			GROUP BY activity_type
			ORDER BY activity_type ASC""", {"start_time":start_date,"end_time": end_date}, as_dict=1):
		columns.append({
			"fieldname": "activity_" + cstr(i),
			"label": activity.activity_type,
			"fieldtype": "Float",
			"options": "",
			"width": 120
		})
		i+=1
	
	columns.append({
		"fieldname": "total_hours",
		"label": "Total Hours",
		"fieldtype": "Float",
		"options": "",
		"width": 120
	})
	#columns.append({
	#	"fieldname": "overtime_hours",
	#	"label": "Overtime Hours",
	#	"fieldtype": "Float",
	#	"options": "",
	#	"width": 140
	#})



	return columns
	
	
def get_holidays_for_employee(employee, start_date, end_date):
	holiday_list = get_holiday_list_for_employee(employee)
	holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
		where
			parent=%(holiday_list)s
			and holiday_date >= %(start_date)s
			and holiday_date <= %(end_date)s''', {
				"holiday_list": holiday_list,
				"start_date": start_date,
				"end_date": end_date
			})

	holidays = [cstr(i) for i in holidays]

	return holidays
