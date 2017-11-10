

frappe.ui.form.on("Purchase Invoice", "validate", function(frm) {
	
	var emp_name = "";
	if ("Employee" in frappe.defaults.get_user_permissions())
	{
		emp_name = frappe.defaults.get_user_permissions().Employee[0];
	} else {
		emp_name = frappe.defaults.get_user_default("Employee") || "";
	}
	if (frm.doc.workflow_state != frm.doc.last_workflow_state) {
		if(frm.doc.last_workflow_state == "Ready for Review" && frm.doc.workflow_state == "Approved by Accounting") {

			for (var property in frm.fields_dict) {
				if (frm.fields_dict.hasOwnProperty(property)) {
					if (property.startsWith('approvalcheck')  && !property.endsWith("1")) {
						if(frm.fields_dict.hasOwnProperty(property + "1"))
						{
							frm.doc[property] = frm.doc[property] | frm.doc[property + "1"];
							frm.doc[property + "1"] = frm.doc[property] | frm.doc[property + "1"];
						}
						if(frm.doc[property] == 0) {
							frappe.validated = false;
							frappe.msgprint(__("Accouting Checklist must be completed before submiting this Purchase Invoice"));
							return;
						}
					}
				}
			}
		}
		if(frm.doc.last_workflow_state == "Approved by Accounting" && frm.doc.workflow_state == "Approved") {

			for (var property in frm.fields_dict) {
				if (frm.fields_dict.hasOwnProperty(property)) {
					if (property.startsWith('purchasecheck')  && !property.endsWith("1")) {
						if(frm.fields_dict.hasOwnProperty(property + "1"))
						{
							frm.doc[property] = frm.doc[property] | frm.doc[property + "1"];
							frm.doc[property + "1"] = frm.doc[property] | frm.doc[property + "1"];
						}
						if(frm.doc[property] == 0) {
							frappe.validated = false;
							frappe.msgprint(__("Purchasing Checklist must be completed before submiting this Purchase Invoice"));
							return;
						}
					}
				}
			}
			if(emp_name != frm.doc.approver) {
				frappe.validated = false;
				frappe.msgprint(__("Only the authorized Purchase Invoice  Approver can approve this invoice. Please make sure you inform the approver they need to review this document by assigning them to it (Assign +)."));
				return;
			}
		}
	}
	frm.doc.last_workflow_state = frm.doc.workflow_state;
	
});
			
frappe.ui.form.on("Purchase Invoice", "onload", function(frm) {
	if (frm.doc.__unsaved == undefined)
	{
		frm.toggle_display("approver",true);
		frm.set_query("approver", function(doc) {
			console.log("getting");
			return{
				query: "velometro.velometro.purchase_order.get_valid_invoice_approvers",
				filters: {'name': doc.name}
			}
		});
	}
	
});


frappe.ui.form.on("Purchase Invoice", "refresh", function(frm) {

	//In the pending workflow
	var showApprovals = 0;
	var emp_name = "";
	if ("Employee" in frappe.defaults.get_user_permissions())
	{
		emp_name = frappe.defaults.get_user_permissions().Employee[0];
	} else {
		emp_name = frappe.defaults.get_user_default("Employee") || "";
	}
	if(frm.doc.workflow_state == "Ready for Review") {
		showApprovals = 1;
		frm.add_custom_button(__('Accounting Checklist'), function(doc){
			var cbs = []
			for (var property in frm.fields_dict) {
				if (frm.fields_dict.hasOwnProperty(property)) {
					if (property.startsWith('approvalcheck') && !property.endsWith("1")) {
						cbs.push({fieldname: frm.fields_dict[property].df.fieldname, label: __(frm.fields_dict[property].df.label),fieldtype: frm.fields_dict[property].df.fieldtype, 'default': frm.doc[property]});
					}
				}
			}
			
			frappe.prompt(cbs,
				function (values) {	
					var pass = 1;
					for (var property in values) {
						if (values.hasOwnProperty(property) && frm.fields_dict.hasOwnProperty(property)) {
							frm.doc[property] = values[property];
							if (values[property] != 1) {
								pass = 0;
							}
							if (frm.fields_dict.hasOwnProperty(property + "1")) {
								frm.doc[property+"1"] = values[property];
							}
						}
					}
					
					frm.save();
					return;
				},					
			 __('Approval Checklist'),__('Save'));
		});
	}
	else if(frm.doc.workflow_state == "Approved by Accounting" && emp_name == frm.doc.approver) {
		
		showApprovals = 2;
		frm.add_custom_button(__('Purchasing Checklist'), function(doc){
			var cbs = []
			for (var property in frm.fields_dict) {
				if (frm.fields_dict.hasOwnProperty(property)) {
					if (property.startsWith('purchasecheck')&& !property.endsWith("1")) {
						cbs.push({fieldname: frm.fields_dict[property].df.fieldname, label: __(frm.fields_dict[property].df.label),fieldtype: frm.fields_dict[property].df.fieldtype, 'default': frm.doc[property]});
					}
				}
			}
			
			frappe.prompt(cbs,
				function (values) {	
					var pass = 1;
					for (var property in values) {
						if (values.hasOwnProperty(property) && frm.fields_dict.hasOwnProperty(property)) {
							frm.doc[property] = values[property];
							if (values[property] != 1) {
								pass = 0;
							}
							if (frm.fields_dict.hasOwnProperty(property + "1")) {
								frm.doc[property+"1"] = values[property];

							}
						}
					}
					
					frm.save();
					return;
				},					
			 __('Approval Checklist'),__('Save'));
		});
	}
	else if(frm.doc.workflow_state == "Approved") {
		showApprovals = 3;
	}
	for (var property in frm.fields_dict) {
		if (frm.fields_dict.hasOwnProperty(property)) {
			if (property.startsWith('approvalcheck')) {
				
				if (showApprovals < 1) {
					frm.set_value(property, 0);
				}
				if (showApprovals != 1) {
					frm.toggle_display(property,false);
				}
				else {
					frm.toggle_display(property,true);
				}
			}
			if (property.startsWith('purchasecheck')) {
				if (showApprovals < 2)	{
					frm.set_value(property, 0);
				}
				if (showApprovals != 2) {
					frm.toggle_display(property,false);
				}
				else {
					frm.toggle_display(property,true);
				}

			}
		}
	}
	
	
});
