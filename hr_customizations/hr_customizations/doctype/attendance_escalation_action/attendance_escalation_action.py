# Copyright (c) 2026, Ahmed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days


class AttendanceEscalationAction(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        action: DF.Literal["Deduct Leave Day", "Deduct Salary Day", "No Action"]
        amended_from: DF.Link | None
        employee: DF.Link | None
        escalated_by: DF.Link | None
        escalation_date: DF.Datetime | None
        leave_type_for_deduction: DF.Link | None
        month: DF.Data | None
        rejection_warning_count: DF.Int
        salary_component_for_deduction: DF.Link | None
        year: DF.Int
    # end: auto-generated types

    def on_submit(self):
        if self.action == "Deduct Leave Day":
            self.deduct_leave()
        elif self.action == "Deduct Salary Day":
            self.deduct_salary()
    
    def before_cancel(self):
        entries = frappe.get_all(
            "Leave Ledger Entry",
            filters={
                "transaction_name": self.name,
                "transaction_type": self.doctype,
                "docstatus": 1
            },
            pluck="name"
        )

        for entry in entries:
            frappe.db.set_value("Leave Ledger Entry", entry.name, "is_expired", True)
            frappe.db.commit()
            doc = frappe.get_doc("Leave Ledger Entry", entry)
            doc.cancel()

    
    def deduct_leave(self):
        if not self.employee or not self.leave_type_for_deduction:
            frappe.throw("Employee and Leave Type are required")

        action_date = nowdate()

        leave_ledger_entry_doc = frappe.new_doc("Leave Ledger Entry")
        leave_ledger_entry_doc.update({
            'employee': self.employee,
            'leave_type': self.leave_type_for_deduction,
            'from_date': action_date,
            'to_date': action_date,
            'leaves': -1,
            'transaction_type': self.doctype,
            'transaction_name': self.name,
        })
        leave_ledger_entry_doc.submit()
        

        frappe.logger().info(f"Leave deducted for {self.employee}")


    def deduct_salary(self):
        if not self.employee or not self.salary_component_for_deduction:
            frappe.throw("Employee and Salary Component are required")

        base_salary = frappe.db.get_value("Salary Structure Assignment", 
        {"employee": self.employee, "docstatus": 1}, "base")

        if not base_salary:
            frappe.throw(f"No active Salary Structure Assignment found for {self.employee}")

        total_working_days = 30

        amount_to_deduct = (base_salary) / total_working_days

        additional_salary = frappe.get_doc({
            "doctype": "Additional Salary",
            "employee": self.employee,
            "salary_component": self.salary_component_for_deduction,
            "amount": amount_to_deduct,
            "payroll_date": nowdate(),
            "ref_doctype": self.doctype,
            "ref_docname": self.name,
            "remarks": f"Auto deduction from escalation {self.name}"
        })

        additional_salary.insert(ignore_permissions=True)
        additional_salary.submit()

        frappe.logger().info(f"Salary deducted for {self.employee}")


