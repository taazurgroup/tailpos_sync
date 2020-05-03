# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = [
		{"fieldname": "store_name", "label": "Store Name", "fieldtype": "Data", "width": 150},
		{"fieldname": "date", "label": "Date", "fieldtype": "Data", "width": 100},
		{"fieldname": "invoice_number", "label": "Invoice Number", "fieldtype": "Data", "width": 150},
		{"fieldname": "net_sale", "label": "Net Sale", "fieldtype": "Data", "width": 100},
		{"fieldname": "discount", "label": "Discount", "fieldtype": "Data", "width": 100},
		{"fieldname": "loyalty", "label": "Loyalty", "fieldtype": "Data", "width": 100},
		{"fieldname": "round_off", "label": "Round Off", "fieldtype": "Data", "width": 100},
		{"fieldname": "vat", "label": "VAT", "fieldtype": "Data", "width": 100},
		{"fieldname": "grand_total", "label": "Grand Total", "fieldtype": "Data", "width": 100},
	]
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	store = filters.get("store")

	data = frappe.db.sql(
		""" SELECT 
 				D.device_name as store_name,
 				SI.posting_date as date,
 				SI.name as invoice_number,
 				SI.total as net_sale,
 				SI.discount_amount as discount,
 				SI.write_off_amount as round_off,
 				SI.grand_total as grand_total,
 				SI.status as status
 			FROM `tabSales Invoice` as SI
 			INNER JOIN `tabDevice` as D ON D.name = %s
 			WHERE posting_date BETWEEN %s and %s """, (store,from_date,to_date), as_dict=True)
	for datum in data:
		sales_invoice_payments = frappe.db.sql(""" SELECT * FROM `tabSales Invoice Payment` WHERE parent=%s""",datum.invoice_number, as_dict=True)
		for i in sales_invoice_payments:

			add = True
			for ii in columns:
				if ii.get("fieldname") == i.mode_of_payment:
					add = False
			if add:
				columns.append({
					"fieldname": i.mode_of_payment,
					"label": i.mode_of_payment,
					"fieldtype": "Data",
					"width": 150
				})
			datum[i.mode_of_payment] = i.amount
	columns.append({
		"fieldname": "status",
		"label": "Status",
		"fieldtype": "Data",
		"width": 100
	})

	return columns, data
