# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []


	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	store = filters.get("store")
	category = filters.get("category")
	if not store:
		columns.append({"fieldname": "store_name", "label": "Store Name", "fieldtype": "Data", "width": 150},)
	if category:
		data = get_receipts_category(category,store)
	else:
		columns.append({"fieldname": "category", "label": "Category", "fieldtype": "Data", "width": 150})
		data = get_receipts(store)

	columns.append({"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 150})
	columns.append({"fieldname": "uom", "label": "UOM", "fieldtype": "Data", "width": 150})
	columns.append({"fieldname": "qty", "label": "QTY", "fieldtype": "Data", "width": 150})
	columns.append({"fieldname": "vat", "label": "VAT", "fieldtype": "Data", "width": 150})
	columns.append({"fieldname": "gross_amount", "label": "Gross Amount", "fieldtype": "Data", "width": 150})

	return columns, data

def get_receipts(store):
	condition = ""
	if store:
		condition += " WHERE name='{0}'".format(store)
	query = """ SELECT * FROM `tabDevice` {0}""".format(condition)
	stores = frappe.db.sql(query,as_dict=1)
	data = []
	for ii in stores:
		categories = frappe.db.sql(""" SELECT * FROM `tabCategories` """, as_dict=1)

		for i in categories:
			data.extend(get_receipts_category(i.name, ii.name))
	return data
def get_receipts_category(category,store):
	conditions = ""
	if store:
		device = frappe.db.sql(""" SELECT * FROM `tabDevice` WHERE name = %s """,store,as_dict=1)
		conditions += " WHERE R.deviceid = '{0}'".format(store)
		store = device[0].device_name
	query = """ 
 				SELECT RI.item,RI.item_name,RI.qty, RI.item_total_tax as vat FROM `tabReceipts` as R
 				INNER JOIN `tabReceipts Item` as RI ON RI.parent = R.name
 				INNER JOIN `tabItem` as I ON I.name = RI.item and I.category = '{0}'
 				{1}
  			""".format(category, conditions)
	print(query)
	receipts = frappe.db.sql(query, as_dict=True)
	data = []
	for idx,i in enumerate(receipts):
		add = True
		for ii in data:

			if i.item_name == ii.get("item_name"):
				add = False
				ii["qty"] += float(i.qty)
				ii["vat"] += float(round(i.vat,2))
		if add:
			data.append({
				"qty": float(i.qty),
				"vat": float(round(i.vat,2)),
				"item_name": i.item_name,
				"item": i.item,
				"category": category if idx == 0 else "",
				"store_name": store if idx == 0 else ""
			})
	for ii in data:
		uom = frappe.db.sql(""" SELECT * FROM `tabUOM Conversion Detail` WHERE parent=%s """, ii.get("item"), as_dict=True)
		if len(uom) > 0:
			ii['uom'] = uom[0].uom
	print(receipts)
	print(data)
	return data