from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime
from datetime import timedelta
from frappe.utils import flt, getdate, rounded, date_diff, getdate

@frappe.whitelist(allow_guest=True)
def validate_annual_leave_settlement(self,method):
    if self.salary_component=="Annual Leave settlement":
        if (not self.ind_last_settlement_date or not self.ind_settlement_date or not self.ind_ssa):
            frappe.throw(_("Select SSA, Settlement Date, Last Settlement Date"))
#        self.overwrite_salary_structure_amount=1
        self.ind_service_period=date_diff(self.ind_settlement_date,self.ind_last_settlement_date)
        self.ind_service_years=self.ind_service_period/365

        self.amount=(self.ind_basic_salary+self.ind_hra)*self.ind_service_period/365*(self.ind_annual_earned_days/30)
#        last_ssa = frappe.get_list("Salary Structure Assignment",
#    	    fields=["from_date", "employee","name"],
#		    filters = {
#		        "employee": self.employee,
#                        "name": ("<=",self.ind_ssa),
#		        "name": ("!=", self.name)
#            })
#        self.ind_ssa=last_ssa[0].name


@frappe.whitelist(allow_guest=True)
def calculate_esb_settlement(self,method):
    if self.salary_component=="End of Service Benefits":
        self.overwrite_salary_structure_amount=1
        self.ind_service_period=date_diff(self.ind_settlement_date,self.ind_joining_date)
        self.ind_service_years=self.ind_service_period/365
        if (not self.ind_settlement_date or not self.ind_reason_for_esb_settlement):
            frappe.throw(_("Please select, Settlement Date and Reason for ESB Settlement"))

        if (self.ind_service_period<730):
            self.ind_esb_category="below 2 years"
            if self.ind_reason_for_esb_settlement=="End of Contract":
                self.amount=self.ind_gross_salary*0.50*self.ind_service_years
            elif self.ind_reason_for_esb_settlement=="Termination":
                self.amount=self.ind_gross_salary*0.50*self.ind_service_years+2*self.ind_basic_salary
            elif self.ind_reason_for_esb_settlement=="Resignation":
#                self.amount=self.ind_gross_salary*0.50*self.ind_service_years
                self.amount=self.ind_gross_salary*0

        elif (self.ind_service_period>729 and self.ind_service_period<1825):
            self.ind_esb_category="2-5 years"
            if self.ind_reason_for_esb_settlement=="Resignation":
                self.amount=self.ind_gross_salary*0.166*self.ind_service_years

            elif self.ind_reason_for_esb_settlement=="End of Contract":
                self.amount=self.ind_gross_salary*0.50*self.ind_service_years

            elif self.ind_reason_for_esb_settlement=="Termination":
                self.amount=self.ind_gross_salary*0.50*self.ind_service_years+2*self.ind_basic_salary


        elif (self.ind_service_period>1824 and self.ind_service_period<3650):
            self.ind_esb_category="5-10 years"
            self.ind_service_years_after_5_years=self.ind_service_years-5
            if self.ind_reason_for_esb_settlement=="Resignation":
                self.amount=self.ind_gross_salary*0.33*5+self.ind_gross_salary*0.667*self.ind_service_years_after_5_years
            elif self.ind_reason_for_esb_settlement=="Termination":
                self.amount=self.ind_gross_salary*0.50*5+self.ind_gross_salary*self.ind_service_years_after_5_years+2*self.ind_basic_salary
            elif self.ind_reason_for_esb_settlement=="End of Contract":
                self.amount=self.ind_gross_salary*0.50*5+self.ind_gross_salary*self.ind_service_years_after_5_years

        elif (self.ind_service_period>3649):
            self.ind_esb_category="above 10 years"
            self.ind_service_years_after_5_years=self.ind_service_years-5
            if self.ind_reason_for_esb_settlement=="Resignation":
                self.amount=self.ind_gross_salary*0.50*5+self.ind_gross_salary*self.ind_service_years_after_5_years
            elif self.ind_reason_for_esb_settlement=="End of Contract":
                self.amount=self.ind_gross_salary*0.50*5+self.ind_gross_salary*self.ind_service_years_after_5_years
            elif self.ind_reason_for_esb_settlement=="Termination":
                self.amount=self.ind_gross_salary*0.50*5+self.ind_gross_salary*self.ind_service_years_after_5_years+2*self.ind_basic_salary
def calculate_overtime(self,method):
    if self.salary_component=="Over Time":
        self.ind_gross_salary_per_hour=self.ind_basic_salary/300
        self.amount=self.ind_overtime_hours*self.ind_overtime_rate*self.ind_basic_salary_per_hour
