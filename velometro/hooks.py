# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "velometro"
app_title = "Velometro"
app_publisher = "Velometro Mobility Inc"
app_description = "Contains all of the Velometro specific documents and forms."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "bcornwellmott@velometro.com"
app_version = "0.0.1"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/velometro/css/velometro.css"
# app_include_js = "/assets/velometro/js/velometro.js"

# include js, css files in header of web template
# web_include_css = "/assets/velometro/css/velometro.css"
# web_include_js = "/assets/velometro/js/velometro.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "velometro.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "velometro.install.before_install"
# after_install = "velometro.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "velometro.notifications.get_notification_config"

# Fixtures
# --------
fixtures = [{"doctype":"Custom Field", "filters": [["name", "!=", "Supplier-octopart_seller_name"]]}, "Custom Script"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Timesheet": {
		"on_submit": "velometro.velometro.vacation.check_for_new_leave"
	},
    "Item": {
		"before_save": "velometro.velometro.inventor_integration.update_description"
	}
  
}

 

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"velometro.tasks.all"
# 	],
# 	"daily": [
# 		"velometro.tasks.daily"
# 	],
# 	"hourly": [
# 		"velometro.tasks.hourly"
# 	],
# 	"weekly": [
# 		"velometro.tasks.weekly"
# 	]
# 	"monthly": [
# 		"velometro.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "velometro.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "velometro.event.get_events"
# }

