# Copyright (c) 2013, Velometro Mobility Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import openpyxl
from frappe.utils import date_diff, cstr
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.hr.doctype.process_payroll.process_payroll import get_month_details
from frappe.desk.query_report import run, get_columns_dict
from six import string_types


def execute(filters=None):
	columns, data = [], []
	if filters.employee and filters.fiscal_year:
		columns = get_columns()
		data = get_hours(filters.employee, filters.fiscal_year)

	return columns, data

@frappe.whitelist()
def export_all(employee, year):

	wb = openpyxl.Workbook(write_only=False)
	
	if (employee is None) or (employee == "") or (employee == "null"):
		employee_list = frappe.get_list("Employee")
	else:
		employee_list = [employee]
	
	if (year is None) or (year == "") or (year == "null"):
		year_list = frappe.get_list("Fiscal Year")
	else:
		year_list = [year]
	
	for emp in employee_list:
		for yr in year_list:
			empn = frappe.get_value("Employee", emp, "employee_name")
			yearn = frappe.get_value("Fiscal Year", yr, "year")
			ws = str(empn) + " (" + str(yearn) + ")"
			frappe.msgprint("Exporting " + ws)
			export_my_query({'employee':emp, 'fiscal_year':yr}, ws, wb)
	
def export_my_query(filters, ws=None,wb=None):

	data = frappe._dict(frappe.local.form_dict)
	del data["cmd"]
	if "csrf_token" in data:
		del data["csrf_token"]
		
	if isinstance(data.get("report_name"), string_types):
		report_name = data["report_name"]
	if isinstance(data.get("visible_idx"), string_types):
		visible_idx = json.loads(data.get("visible_idx"))
	else:
		visible_idx = None
	
	data = run("Employee Yearly Summary", filters)
	data = frappe._dict(data)
	columns = get_columns_dict(data.columns)

	result = [[]]

	# add column headings
	for idx in range(len(data.columns)):
		result[0].append(columns[idx]["label"])

	# build table from dict
	if isinstance(data.result[0], dict):
		for i,row in enumerate(data.result):
			# only rows which are visible in the report
			if row:
				row_list = []
				for idx in range(len(data.columns)):
					row_list.append(row.get(columns[idx]["fieldname"],""))
				result.append(row_list)
			elif not row:
				result.append([])
	else:
		result = result + [d for i,d in enumerate(data.result) if (i+1 in visible_idx)]

	from frappe.utils.xlsxutils import make_xlsx
	if ws is None:
		ws = "Query Report"
	xlsx_file = make_xlsx(result, ws, wb)
	
	frappe.response['filename'] = report_name + '.xlsx'
	frappe.response['filecontent'] = xlsx_file.getvalue()
	frappe.response['type'] = 'binary'

def get_hours(employee, fiscal_year):
	out = []
	month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	
	# set up data for last column
	ytd_total = 0
	ytd_vacation = 0
	ytd_stat = 0
	ytd_lieu = 0
	ytd_sick = 0
	ytd_ot = 0
	
	# Get the hours from all previous years
	prev_total_hrs = 0
	prev_vacation_hrs = 0
	prev_sick_hrs = 0
	prev_stat_hrs = 0
	prev_lieu_hrs = 0
	prev_ot_hrs = 0

	m = get_month_details(fiscal_year, 1)
	start_date = m['month_start_date']
	current_date = frappe.utils.getdate(frappe.utils.nowdate())

	for timesheet_hrs in frappe.db.sql("""select detail.hours as hours, detail.activity_type as type from `tabTimesheet Detail` as detail, `tabTimesheet` as sheet where detail.from_time < %(start_time)s and detail.parent = sheet.name and sheet.docstatus = 1 and sheet.employee = %(employee)s""", {"employee": employee, "start_time":start_date}, as_dict=1):
		prev_total_hrs += timesheet_hrs.hours
		if "Vacation" in timesheet_hrs.type:
			prev_vacation_hrs += timesheet_hrs.hours
		if "Stat Holiday" in timesheet_hrs.type:
			prev_stat_hrs += timesheet_hrs.hours
		if "Sick" in timesheet_hrs.type:
			prev_sick_hrs += timesheet_hrs.hours
		if "Lieu" in timesheet_hrs.type:
			prev_lieu_hrs += timesheet_hrs.hours
			prev_total_hrs -= timesheet_hrs.hours
				
	#Get the starting value working days
	joining_date = frappe.db.get_value("Employee", employee,["date_of_joining"])
	holidays = get_holidays_for_employee(employee, joining_date, start_date)
	if start_date >= joining_date:
		working_days = date_diff(start_date, joining_date) - len(holidays)
	else:
		working_days = 0
	prev_ot_hrs = max(0,prev_total_hrs - 8 * working_days)

				
	row = frappe._dict({
		"month": "START OF YEAR",
		"working_days": 0,
		"total_hours": prev_total_hrs,
		"vacation_hours": prev_vacation_hrs,
		"sick_hours": prev_sick_hrs,
		"statutory_hours": prev_stat_hrs,
		"lieu_hours": prev_lieu_hrs,
		"overtime_hours": prev_ot_hrs
		})
	out.append(row)
	# Do each month
	for month in month_list:
		total_hrs = 0
		vacation_hrs = 0
		sick_hrs = 0
		stat_hrs = 0
		lieu_hrs = 0
		ot_hrs = 0
		index = month_list.index(month)
		m = get_month_details(fiscal_year, index+1)
		start_date = m['month_start_date']
		end_date = m['month_end_date']
		for timesheet_hrs in frappe.db.sql("""SELECT detail.hours as hours, detail.activity_type as type 
			FROM `tabTimesheet Detail` as detail, `tabTimesheet` as sheet 
			WHERE cast(detail.from_time as date) BETWEEN %(start_time)s AND %(end_time)s AND 
			detail.parent = sheet.name AND 
			sheet.docstatus = 1 AND 
			sheet.employee = %(employee)s""", {"employee": employee, "start_time":start_date, "end_time": end_date}, as_dict=1):
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
			if "Lieu" in timesheet_hrs.type:
				lieu_hrs += timesheet_hrs.hours
				ytd_lieu += timesheet_hrs.hours
				total_hrs -= timesheet_hrs.hours
				ytd_total -= timesheet_hrs.hours
				
		#Get the hours in each month you're supposed to work
		if end_date > current_date:
			end_date = current_date
		if end_date > start_date:
			month_start_date = start_date if start_date < joining_date else joining_date
			holidays = get_holidays_for_employee(employee, month_start_date, end_date)
			if start_date >= joining_date:
				working_days = date_diff(end_date, start_date) + 1 - len(holidays)
			elif end_date >= joining_date:
				working_days = date_diff(end_date, joining_date) + 1 - len(holidays)
			else:
				working_days = 0
		else:
			working_days = 0
		
		if working_days > 0:
			ot_hrs = max(0,total_hrs - 8 * working_days)
		else:
			ot_hrs = 0
		#if ot_hrs < 0:
		#	ot_hrs = 0
		#ot_hrs -= lieu_hrs
		
		ytd_ot += ot_hrs 
		row = frappe._dict({
				"month": month,
				"working_days": working_days,
				"total_hours": total_hrs,
				"vacation_hours": vacation_hrs,
				"sick_hours": sick_hrs,
				"statutory_hours": stat_hrs,
				"lieu_hours": lieu_hrs,
				"overtime_hours": ot_hrs
			})
		out.append(row)
	row = frappe._dict({
		"month": "YEAR TO DATE",
		"working_days": 0,
		"total_hours": ytd_total,
		"vacation_hours": ytd_vacation,
		"sick_hours": ytd_sick,
		"statutory_hours": ytd_stat,
		"lieu_hours": ytd_lieu,
		"overtime_hours": ytd_ot
		})
	out.append(row)
	row = frappe._dict({
		"month": "GRAND TOTAL",
		"total_hours": ytd_total + prev_total_hrs,
		"working_days": 0,
		"vacation_hours": ytd_vacation + prev_vacation_hrs,
		"sick_hours": ytd_sick + prev_sick_hrs,
		"statutory_hours": ytd_stat + prev_stat_hrs,
		"lieu_hours": ytd_lieu + prev_lieu_hrs,
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
		"fieldname": "working_days",
		"label": "Working Days",
		"fieldtype": "Float",
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
		"fieldname": "lieu_hours",
		"label": "Time in Lieu",
		"fieldtype": "Float",
		"options": "",
		"width": 140
	},{
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
