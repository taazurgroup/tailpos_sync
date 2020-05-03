import frappe


def update_loyalty_programs(doc, method):
    frappe.db.sql(""" UPDATE `tabLoyalty Program` as LP SET LP.default=0 WHERE name != %s """, doc.name)
    frappe.db.commit()