// Copyright (c) 2016, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Wise Sales Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1

		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "store",
			"label": __("Store"),
			"fieldtype": "Link",
			"options": "Device",
			"reqd": 1
		},
		{
			"fieldname": "category",
			"label": __("Category"),
			"fieldtype": "Link",
			"options": "Category",
		}
	]
};
