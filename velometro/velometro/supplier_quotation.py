
from __future__ import unicode_literals

import frappe
from frappe import _, throw
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item, get_pricing_rules, filter_pricing_rules, apply_pricing_rule
from frappe.utils import flt
import json

@frappe.whitelist()
def add_pricing_rules(mquotation, method=None):
	"""This function adds all the items to pricing rules"""
	frappe.msgprint(_("Adding Pricing Rules"))
	quotation = frappe.get_doc("Supplier Quotation",mquotation)
	
	# Loop through all of the items in the price list 
	for item_doc in quotation.items:
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
			new_rule = frappe.get_doc({"doctype":"Pricing Rule", "min_qty": item_doc.qty, "apply_on": "Item Code", "item_code": item_doc.item_code, "priority": 1, "buying": "1", "applicable_for": "Supplier", "company": quotation.company, "price_or_discount": "Price", "price": item_doc.rate, "supplier": quotation.supplier, "for_price_list" : quotation.buying_price_list, "title": pr_title, "from_supplier_quotation": quotation.name })
			new_rule.insert()

		else:
			frappe.msgprint(_("Pricing Rule {0} applies for this item".format(pr_result.pricing_rule)))
			
			# Check to see if the pricing rule matches quantity min exactly
			pricing_rule = frappe.get_doc("Pricing Rule", pr_result.pricing_rule)
			if item_doc.qty == pricing_rule.min_qty:
				# This pricing rule rate just needs to be changed
				frappe.msgprint(_("Updating Pricing Rule"))
				frappe.set_value("Pricing Rule", pricing_rule.name, "price",item_doc.rate)
				frappe.set_value("Pricing Rule", pricing_rule.name, "from_supplier_quotation",quotation.name)

			else:
				frappe.msgprint(_("Creating new rule and incrementing priority"))
				# This rule is lower in qty than the current rule. We need to add a new pricing rule and update the priorities for each of the higher quantity pricing rules
				pr_title = item_doc.item_code + "-" + quotation.supplier + "-" + str(item_doc.qty)
				new_rule = frappe.get_doc({"doctype":"Pricing Rule", "min_qty": item_doc.qty, "apply_on": "Item Code", "item_code": item_doc.item_code, "priority": pricing_rule.priority, "buying": "1", "applicable_for": "Supplier", "company": quotation.company, "price_or_discount": "Price", "price": item_doc.rate, "supplier": quotation.supplier, "for_price_list" : quotation.buying_price_list, "title": pr_title, "from_supplier_quotation": quotation.name })
				new_rule.insert()

				# Run through each of the higher quantity pricing rules and increase their priority by one 
				unfiltered_rules = get_pricing_rules(args)
				pricing_rules = filter(lambda x: (flt(item_doc.qty)<=flt(x.min_qty)), unfiltered_rules)
				for pr in pricing_rules:
					frappe.set_value("Pricing Rule", pr.name, "priority",str(int(pr.priority) + 1))
					#frappe.msgprint(_("Incorporating new Pricing rule between others".format(pr.name, pr.priority))) 


@frappe.whitelist()
def copy_pricing_rule_from_previous_revision(base_item_code, current_rev):
	"""This function adds all the items to pricing rules"""
	
	args = {
		
		"item_code": str(base_item_code) + "_" + str(int(current_rev)-1), 
		"transaction_type": "buying"
	}
	
	
	args = frappe._dict(args)
	frappe.msgprint(_("Copying Pricing Rules for " + args.item_code))
	pr_result = get_pricing_rules(args) 
	
	for myrule in pr_result:
		frappe.msgprint(_("Copying Pricing Rule " + myrule.pricing_rule))
		# Check to see if the pricing rule matches quantity min exactly
		rule = frappe.get_doc("Pricing Rule", myrule.pricing_rule)
		pr_title = item_doc.item_code + "-" + quotation.supplier + "-" + str(item_doc.qty)
		new_rule = frappe.get_doc({"doctype":"Pricing Rule", "min_qty": rule.min_qty, "apply_on": rule.apply_on, "item_code": args.item_code, "priority": rule.priority, "buying": rule.buying, "applicable_for": rule.applicable_for, "company": rule.company, "price_or_discount": rule.price_or_discount, "price": rule.price, "supplier": rule.supplier, "for_price_list" : rule.for_price_list, "title": pr_title, "from_supplier_quotation": rule.from_supplier_quotation })
		new_rule.insert()

