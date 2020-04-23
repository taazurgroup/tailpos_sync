# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []

	columns.append({"fieldname": "invoice", "label": "Invoice", "fieldtype": "Link","options": "Purchase Invoice", "width": 150})
	columns.append({"fieldname": "posting_date", "label": "Discount", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "supplier_name", "label": "Supplier Name", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "mode_of_payment", "label": "Mode of Payment", "fieldtype": "Data", "width": 160})
	columns.append({"fieldname": "net_total", "label": "Net Total", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "vat", "label": "VAT 5%", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "grand_total", "label": "Grand Total", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "rounded_total", "label": "Rounded Total", "fieldtype": "Data", "width": 130})
	columns.append({"fieldname": "outstanding_amount", "label": "Outstanding Amount", "fieldtype": "Data", "width": 160})
	columns.append({"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "remarks", "label": "Remarks", "fieldtype": "Data", "width": 100})

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	cost_center = filters.get("cost_center")
	accounts_ledger = filters.get("accounts_ledger")
	conditions = ""
	print(cost_center)
	if cost_center:
		conditions += " and cost_center = '{0}'".format(cost_center)
	if accounts_ledger:
		conditions += " and credit_to = '{0}'".format(accounts_ledger)
	query = """ SELECT * FROM `tabPurchase Invoice` WHERE docstatus=1 and posting_date BETWEEN '{0}' and '{1}' {2}""".format(from_date, to_date, conditions)
	print(query)
	purchase_invoice = frappe.db.sql(query, as_dict=True)
	for i in purchase_invoice:
		vat = frappe.db.sql(""" 
 					SELECT * FROM `tabPurchase Taxes and Charges` 
 					WHERE parent=%s and account_head LIKE %s""", (i.name, "VAT 5%%"), as_dict=True)
		data.append({
			"invoice": i.name,
			"posting_date":i.posting_date,
			"supplier_name":i.supplier_name,
			"mode_of_payment":"Cash",
			"net_total":i.total,
			"vat":vat[0].tax_amount if len(vat) > 0 else 0.00,
			"grand_total":i.grand_total,
			"rounded_total":i.rounded_adjustment,
			"outstanding_amount":i.outstanding_amount,
			"status":i.status,
			"remarks":i.remarks,
		})
	return columns, data
