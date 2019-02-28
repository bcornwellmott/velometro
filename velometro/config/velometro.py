from frappe import _

def get_data():
	return [
		{
			"label": _("Controlled Documents"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Procedure",
					"description": _("All the released procedures to follow."),
				},
				{
					"type": "doctype",
					"name": "Work Instructions",
					"description": _("All the work instructions."),
				},
				
			]
		},{
			"label": _("Performance Evaluations"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Performance Evaluation",
					"label": _("Performance Evaluation Submissions"),
					"description": _("The weekly performance evaluations that get submitted by employees"),
				},
				{
					"type": "doctype",
					"name": "Performance Report",
					"description": _("The reports submitted to each manager summarizing the performance evaluations"),
				},
				{
					"type": "doctype",
					"name": "Performance Meeting",
					"description": _("The meetings and resulting action items regarding performance evaluations."),
				},
				
			]
		}
	]