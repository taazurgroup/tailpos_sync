# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	store = filters.get("store")
	condition = ""
	if store:
		condition += " and R.deviceid='{0}'".format(store)
	query = """ 
 			SELECT R.name, PT.type, PT.amount FROM `tabReceipts` as R 
 			INNER JOIN `tabPayments` as P ON P.receipt = R.name
 			INNER JOIN `tabPayment Types` as PT ON PT.parent = P.name
 			WHERE R.date BETWEEN '{0}' and '{1}' {2}""".format(from_date,to_date,condition)
	receipts = frappe.db.sql(query,as_dict=1)
	total_amount = 0
	totals = {}
	percentage = {}
	for i in receipts:
		total_amount += i.amount

		if i.type in totals:
			totals[i.type] += i.amount
		else:
			columns.append({"fieldname": i.type, "label": i.type, "fieldtype": "Data", "width": 150})
			totals[i.type] = i.amount

	columns.append({"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Data", "width": 150})

	for idx,iii in enumerate(totals):
		percentage[iii + str(idx)] = (totals[iii] / total_amount) * 100
		columns.append({"fieldname": iii + str(idx), "label": iii, "fieldtype": "Data", "width": 150})
	if total_amount > 0:
		totals["total_amount"] = total_amount
		totals.update(percentage)
		data.append(totals)

	return columns, data

