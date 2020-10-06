from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, rounded, date_diff, getdate

#@frappe.whitelist(allow_guest=True)
def calculate_days_to_allocate(self,method):
    self.from_date=frappe.defaults.get_user_default("year_start_date")
    self.to_date=frappe.defaults.get_user_default("year_end_date")
    if (self.taa_calculate_days):
        self.taa_difference_days = date_diff(self.from_date, self.ind_date_of_joining)
        self.taa_days_to_be_added = rounded(self.taa_difference_days * self.ind_max_leaves_allowed / 365)
