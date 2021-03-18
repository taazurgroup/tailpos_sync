frappe.query_reports["Non-Saudi Vacation Report"] = {
    "filters":[

    {
    "fieldname":"taa_exit_re_entry_issued",
    "label" :("Exit Re_Entry Issued"),
    "fieldtype":"Select",
    "options":["Yes","No"],
    "default":"No"
    },

    {
    "fieldname":"taa_ticket_issued",
    "label":("Ticket Issued"),
    "fieldtype":"Select",
    "options":["Yes","No"],
    "default":"No"
    },

    {
    "fieldname":"taa_iqama_returned",
    "label":("taa_iqama_returned"),
    "fieldtype":"Select",
    "options":["Yes","No"],
    "default":"No"
    },
    {
    "fieldname":"taa_returned_from_vacation_",
    "label":("Returned From Vacation"),
    "fieldtype":"Select",
    "options":["Yes","No"],
    "default":"No"
    }
]
}
