# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []

	columns = [
		{"fieldname": "store_name", "label": "Store Name", "fieldtype": "Data", "width": 150},
		{"fieldname": "date", "label": "Date", "fieldtype": "Data", "width": 150},
	]
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	store = filters.get("store")
	query = """ 
			SELECT * FROM `tabReceipts`
			WHERE date BETWEEN '{0}' and '{1}' and deviceid='{2}'
	  		""".format(from_date,to_date,store)
	receipts = frappe.db.sql(query,as_dict=True)
	for receipt in receipts:
		if receipt.total_amount > 0:
			obj = {
				"date": receipt.date,
				"vat": receipt.taxesvalue,
				"total_sale": receipt.total_amount
			}
			store_name = frappe.db.sql(""" SELECT * FROM `tabDevice` WHERE name=%s """, receipt.deviceid, as_dict=True)
			if len(store_name) > 0:
				obj["store_name"] = store_name[0].device_name
			categories_totals = []
			percentage_categories = []

			items = frappe.db.sql(""" SELECT * FROM `tabReceipts Item`  WHERE parent=%s""", receipt.name,as_dict=True)
			for item in items:
				get_item = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE name=%s """, item.item ,as_dict=True)
				if len(get_item) > 0:
					add = True
					for category in categories_totals:
						if category['name'] == get_item[0].category:
							add = False
							category['amount'] += float(item.price) * float(item.qty)
					if add:
						categories_totals.append({
							"name": get_item[0].category,
							"amount": float(item.price) * float(item.qty)
						})
			for total in categories_totals:
				add_ = True
				for xxx in columns:
					if xxx.get("fieldname") == total['name']:
						add_ = False
				if add_:
					columns.append({
						"fieldname": total['name'],
						"label": total['name'],
						"fieldtype": "Data",
						"width": 150
					})
				percentage_categories.append({
					"name": total['name'],
					"amount": str((total["amount"] / receipt.total_amount) * 100)
				})

			for ii in categories_totals:
				obj[ii['name']] = ii['amount']

			for iii in percentage_categories:
				obj[iii['name']+"1"] = iii['amount']

			add = True
			add1 = True
			for xxx in columns:
				if xxx.get("fieldname") == "vat":
					add = False
				if xxx.get("fieldname") == "total_sale":
					add1 = False

			if add:
				columns.append({"fieldname": "vat", "label": "VAT", "fieldtype": "Float", "width": 150,"precision": "2"})
			if add1:
				columns.append({"fieldname": "total_sale", "label": "Total Sales", "fieldtype": "Float", "width": 150,"precision": "2"})
			for total1 in percentage_categories:
				add_ = True
				for xxx in columns:
					if xxx.get("fieldname") == total1['name'] + "1":
						add_ = False
				if add_:
					columns.append({
						"fieldname": total1['name'] + "1",
						"label": total1['name'],
						"fieldtype": "Percent",
						"width": 150
					})

			data.append(obj)
	return columns, data
