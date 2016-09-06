# Copyright (c) 2013, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff, cstr
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.hr.doctype.process_payroll.process_payroll import get_month_details


def execute(filters=None):
	columns, data = [], []
	if filters.employee and filters.fiscal_year:
		columns = get_columns()
		data = get_hours(filters.employee, filters.fiscal_year)

	return columns, data

	
def get_hours(employee, fiscal_year):
	out = []
	month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	
	# set up data for last column
	ytd_total = 0
	ytd_vacation = 0
	ytd_stat = 0
	ytd_sick = 0
	ytd_ot = 0
	
	# Get the hours from all previous years
	prev_total_hrs = 0
	prev_vacation_hrs = 0
	prev_sick_hrs = 0
	prev_stat_hrs = 0
	prev_ot_hrs = 0

	m = get_month_details(fiscal_year, 1)
	start_date = m['month_start_date']

	for timesheet_hrs in frappe.db.sql("""select detail.hours as hours, detail.activity_type as type from `tabTimesheet Detail` as detail, `tabTimesheet` as sheet where detail.from_time < %(start_time)s and detail.parent = sheet.name and sheet.docstatus = 1 and sheet.employee = %(employee)s""", {"employee": employee, "start_time":start_date}, as_dict=1):
		prev_total_hrs += timesheet_hrs.hours
		if "Vacation" in timesheet_hrs.type:
			prev_vacation_hrs += timesheet_hrs.hours
		if "Stat Holiday" in timesheet_hrs.type:
			prev_stat_hrs += timesheet_hrs.hours
		if "Sick" in timesheet_hrs.type:
			prev_sick_hrs += timesheet_hrs.hours
				
	#Get the starting value working days
	joining_date = frappe.db.get_value("Employee", employee,["date_of_joining"])
	holidays = get_holidays_for_employee(employee, joining_date, start_date)
	working_days = date_diff(start_date, joining_date) + 1 - len(holidays)
	prev_ot_hrs = prev_total_hrs - 8 * working_days
	if prev_ot_hrs < 0:
		prev_ot_hrs = 0		
				
	row = frappe._dict({
		"month": "START OF YEAR",
		"total_hours": prev_total_hrs,
		"vacation_hours": prev_vacation_hrs,
		"sick_hours": prev_sick_hrs,
		"statutory_hours": prev_stat_hrs,
		"overtime_hours": prev_ot_hrs
		})
	out.append(row)
	# Do each month
	for month in month_list:
		total_hrs = 0
		vacation_hrs = 0
		sick_hrs = 0
		stat_hrs = 0
		ot_hrs = 0
		index = month_list.index(month)
		m = get_month_details(fiscal_year, index+1)
		start_date = m['month_start_date']
		end_date = m['month_end_date']
		
		for timesheet_hrs in frappe.db.sql("""select detail.hours as hours, detail.activity_type as type from `tabTimesheet Detail` as detail, `tabTimesheet` as sheet where detail.from_time BETWEEN %(start_time)s and %(end_time)s and detail.parent = sheet.name and sheet.docstatus = 1 and sheet.employee = %(employee)s""", {"employee": employee, "start_time":start_date, "end_time": end_date}, as_dict=1):
			total_hrs += timesheet_hrs.hours
			ytd_total += timesheet_hrs.hours
			if "Vacation" in timesheet_hrs.type:
				vacation_hrs += timesheet_hrs.hours
				ytd_vacation += timesheet_hrs.hours
			if "Stat Holiday" in timesheet_hrs.type:
				stat_hrs += timesheet_hrs.hours
				ytd_stat += timesheet_hrs.hours
			if "Sick" in timesheet_hrs.type:
				sick_hrs += timesheet_hrs.hours
				ytd_sick += timesheet_hrs.hours
				
		#Get the hours in each month you're supposed to work
		holidays = get_holidays_for_employee(employee, start_date, end_date)
		working_days = date_diff(end_date, start_date) + 1 - len(holidays)
		ot_hrs = total_hrs - 8 * working_days
		if ot_hrs < 0:
			ot_hrs = 0
		
		ytd_ot += ot_hrs
		row = frappe._dict({
				"month": month,
				"total_hours": total_hrs,
				"vacation_hours": vacation_hrs,
				"sick_hours": sick_hrs,
				"statutory_hours": stat_hrs,
				"overtime_hours": ot_hrs
			})
		out.append(row)
	row = frappe._dict({
		"month": "YEAR TO DATE",
		"total_hours": ytd_total,
		"vacation_hours": ytd_vacation,
		"sick_hours": ytd_sick,
		"statutory_hours": ytd_stat,
		"overtime_hours": ytd_ot
		})
	out.append(row)
	row = frappe._dict({
		"month": "GRAND TOTAL",
		"total_hours": ytd_total + prev_total_hrs,
		"vacation_hours": ytd_vacation + prev_vacation_hrs,
		"sick_hours": ytd_sick + prev_sick_hrs,
		"statutory_hours": ytd_stat + prev_stat_hrs,
		"overtime_hours": ytd_ot + prev_ot_hrs
		})
	out.append(row)

	return out
	
def get_columns():
	columns = [{
		"fieldname": "month",
		"label": "Month",
		"fieldtype": "Data",
		"options": "",
		"width": 120
	}, {
		"fieldname": "total_hours",
		"label": "Total Hours",
		"fieldtype": "Float",
		"options": "",
		"width": 120
	}, {
		"fieldname": "vacation_hours",
		"label": "Vacation Hours",
		"fieldtype": "Float",
		"options": "",
		"width": 140
	}, {
		"fieldname": "sick_hours",
		"label": "Sick Hours",
		"fieldtype": "Float",
		"options": "",
		"width": 120
	}, {
		"fieldname": "statutory_hours",
		"label": "Stat Holiday Hours",
		"fieldtype": "Float",
		"options": "",
		"width": 140
	}, {
		"fieldname": "overtime_hours",
		"label": "Overtime Hours",
		"fieldtype": "Float",
		"options": "",
		"width": 140
	}]



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