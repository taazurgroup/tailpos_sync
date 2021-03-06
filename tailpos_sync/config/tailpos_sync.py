# import frappe
from frappe import _

def get_data():
	return [
		{
			"label": _("TailPOS"),
			"items": [
				{
					"type": "doctype",
					"name": "Attendants",
				},
                {
                    "type": "doctype",
                    "name": "Item",
                },
                {
                    "type": "doctype",
                    "name": "Categories",
                },
                {
                    "type": "doctype",
                    "name": "Discounts",
                },
                {
                    "type": "doctype",
                    "name": "Receipts",
                },
                {
                    "type": "doctype",
                    "name": "Payments",
                },
                {
                    "type": "doctype",
                    "name": "Shifts",
                },
                {
                    "type": "doctype",
                    "name": "Device",
                },
                {
                    "type": "doctype",
                    "name": "Tail Settings",
                },
                
                {
                    "type": "report",
                    "is_query_report": True,
                    "name":"Custom Leave Ledger Entry",
                    "doctype":"Leave Ledger Entry"
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name":"Budget Statement",
                    "doctype":"Budget"
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name":"Budget Variance With Percentage Report",
                    "doctype":"Cost Center"
                },

                {
                    "type": "report",
                    "is_query_report": True,
                    "name":"Non-Saudi Vacation Report",
                    "doctype":"Leave Application"
                }

                ]
		}
                ] 
