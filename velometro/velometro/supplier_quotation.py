
from __future__ import unicode_literals

import frappe
from frappe import _, throw
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item, get_pricing_rules, filter_pricing_rules, apply_pricing_rule
from frappe.utils import flt

@frappe.whitelist()
def add_pricing_rules(quotation, method=None):
	"""This function adds all the items to pricing rules (except for qty = 1 item prices)"""
	frappe.msgprint(_("Adding Pricing Rules"))
	
	# Loop through all of the items in the price list 
	for item_doc in quotation.items:
		# Check to see if the quantity is = 1
		if item_doc.qty != 1:
			#  check to see if there are any pricing rules that fall into the specified quantity/supplier
			#frappe.msgprint(_("Checking pricing rules of {0} for previous prices".format(item_doc.item_code)))

			item = frappe.get_doc("Item",item_doc.item_code)

			args = {
				"doctype": item_doc.doctype,
				"parent_type": item_doc.parenttype,
				"name": item_doc.name,
				"item_code": item_doc.item_code, 
				"transaction_type": "buying",
				"supplier": quotation.supplier,
				"qty": item_doc.qty,
				"price_list": quotation.buying_price_list,
				"company": quotation.company 
			}

			args = frappe._dict(args)
			
			pr_result = get_pricing_rule_for_item(args) 
			
			if not pr_result.pricing_rule:
				frappe.msgprint(_("There are no pricing rules for this item"))
				pr_title = item_doc.item_code + "-" + quotation.supplier + "-" + str(item_doc.qty)
				new_rule = frappe.get_doc({"doctype":"Pricing Rule", "min_qty": item_doc.qty, "apply_on": "Item Code", "item_code": item_doc.item_code, "priority": 1, "buying": "1", "applicable_for": "Supplier", "company": quotation.company, "price_or_discount": "Price", "price": item_doc.rate, "supplier": quotation.supplier, "for_price_list" : quotation.buying_price_list, "title": pr_title })
				new_rule.insert()

			else:
				frappe.msgprint(_("Pricing Rule {0} applies for this item".format(pr_result.pricing_rule)))
				
				# Check to see if the pricing rule matches quantity min exactly
				pricing_rule = frappe.get_doc("Pricing Rule", pr_result.pricing_rule)
				if item_doc.qty == pricing_rule.min_qty:
					# This pricing rule rate just needs to be changed
					frappe.msgprint(_("Updating Pricing Rule"))
					frappe.set_value("Pricing Rule", pricing_rule.name, "price",item_doc.rate)

				else:
					frappe.msgprint(_("Creating new rule and incrementing priority"))
					# This rule is lower in qty than the current rule. We need to add a new pricing rule and update the priorities for each of the higher quantity pricing rules
					pr_title = item_doc.item_code + "-" + quotation.supplier + "-" + str(item_doc.qty)
					new_rule = frappe.get_doc({"doctype":"Pricing Rule", "min_qty": item_doc.qty, "apply_on": "Item Code", "item_code": item_doc.item_code, "priority": pricing_rule.priority, "buying": "1", "applicable_for": "Supplier", "company": quotation.company, "price_or_discount": "Price", "price": item_doc.rate, "supplier": quotation.supplier, "for_price_list" : quotation.buying_price_list, "title": pr_title })
					new_rule.insert()

					# Run through each of the higher quantity pricing rules and increase their priority by one 
					unfiltered_rules = get_pricing_rules(args)
					pricing_rules = filter(lambda x: (flt(item_doc.qty)<=flt(x.min_qty)), unfiltered_rules)
					for pr in pricing_rules:
						frappe.set_value("Pricing Rule", pr.name, "priority",str(int(pr.priority) + 1))
						#frappe.msgprint(_("Incorporating new Pricing rule between others".format(pr.name, pr.priority))) 
		else:
			# Check to see if there is an item price for the price list
			ip_list = frappe.get_all("Item Price", fields=["name"],filters={"item_code": item_doc.item_code, "price_list": quotation.buying_price_list}) 
			
			for ip in ip_list: 
				frappe.msgprint(_("Updating {0}".format(ip.name))) 
				frappe.set_value("Item Price", ip.name, "price_list_rate",item_doc.rate)  


				 


