// Copyright (c) 2026, Ahmed and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Rejected Warnings vs Escalation Threshold"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company"
        },
        {
            "fieldname": "employee",
            "label": "Employee",
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "month",
            "label": "Month",
            "fieldtype": "Select",
            "options": [
                "",
                "1","2","3","4","5","6",
                "7","8","9","10","11","12"
            ]
        },
        {
            "fieldname": "year",
            "label": "Year",
            "fieldtype": "Int"
        },
        {
            "fieldname": "only_threshold_reached",
            "label": "Only Threshold Reached",
            "fieldtype": "Check"
        },
        {
            "fieldname": "only_missing_escalation",
            "label": "Only Missing Escalation",
            "fieldtype": "Check"
        }
    ]
};
