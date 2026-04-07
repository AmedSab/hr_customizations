# Copyright (c) 2026, Ahmed and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 120},
        {"label": "Month", "fieldname": "month", "fieldtype": "Int", "width": 80},
        {"label": "Year", "fieldname": "year", "fieldtype": "Int", "width": 80},
        {"label": "Rejected Warning Count", "fieldname": "rejected_count", "fieldtype": "Int", "width": 150},
        {"label": "Escalation Threshold", "fieldname": "threshold", "fieldtype": "Int", "width": 150},
        {"label": "Threshold Reached", "fieldname": "threshold_reached", "fieldtype": "Data", "width": 150},
        {"label": "Escalation Action Exists", "fieldname": "action_exists", "fieldtype": "Data", "width": 170},
        {"label": "Escalation Status", "fieldname": "action_status", "fieldtype": "Data", "width": 150},
        {"label": "Escalation Date", "fieldname": "action_date", "fieldtype": "Date", "width": 120},
    ]


def get_data(filters) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	conditions = ""

	if filters.get("company"):
		conditions += " AND emp.company = %(company)s"
	if filters.get("employee"):
		conditions += " AND aw.employee = %(employee)s"
	if filters.get("month"):
		conditions += " AND MONTH(aw.warning_date) = %(month)s"
	if filters.get("year"):
		conditions += " AND YEAR(aw.warning_date) = %(year)s"

	threshold = frappe.db.get_single_value("HR Customizations Settings", "escalation_rejection_limit") or 0

	query = f"""
        SELECT
            aw.employee,
            emp.employee_name,
            emp.company,
            MONTH(aw.warning_date) as month,
            YEAR(aw.warning_date) as year,
            COUNT(*) as rejected_count
        FROM `tabAttendance Warning` aw
        LEFT JOIN `tabEmployee` emp ON emp.name = aw.employee
        WHERE aw.state = 'Rejected'
        {conditions}
        GROUP BY aw.employee, month, year
    """

	results = frappe.db.sql(query, filters, as_dict=True)

	final_data = []

	for row in results:
		threshold_reached = row.rejected_count >= threshold

		action = frappe.db.get_value(
            "Attendance Escalation Action",
            {
                "employee": row.employee,
                "docstatus": 1
            },
            ["action", "escalation_date"],
            as_dict=True
        )

		action_exists = "Yes" if action else "No"

        # Apply filters
		if filters.get("only_threshold_reached") and not threshold_reached:
			continue

		if filters.get("only_missing_escalation") and action:
			continue
		
		final_data.append({
            "employee": row.employee,
            "employee_name": row.employee_name,
            "company": row.company,
            "month": row.month,
            "year": row.year,
            "rejected_count": row.rejected_count,
            "threshold": threshold,
            "threshold_reached": "Yes" if threshold_reached else "No",
            "action_exists": action_exists,
            "action_status": action.action if action else "",
            "action_date": action.escalation_date if action else ""
        })

	return final_data

	
	



	return [
		["Row 1", 1],
		["Row 2", 2],
	]
