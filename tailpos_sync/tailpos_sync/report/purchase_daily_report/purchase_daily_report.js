// Copyright (c) 2016, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Daily Report"] = {
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
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
		},
		{
			"fieldname": "accounts_ledger",
			"label": __("Accounts Ledger"),
			"fieldtype": "Link",
			"options": "Account",
		}
	]
};
