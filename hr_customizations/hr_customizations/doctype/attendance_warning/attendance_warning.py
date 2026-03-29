# Copyright (c) 2026, Ahmed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AttendanceWarning(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        absent: DF.Check
        actual_in_time: DF.Time | None
        actual_out_time: DF.Time | None
        amended_from: DF.Link | None
        approval_date: DF.Datetime | None
        approval_decision: DF.Literal["Approved", "Rejected"]
        approval_remarks: DF.SmallText | None
        approver: DF.Link | None
        attendance: DF.Link | None
        company: DF.Link | None
        custom: DF.Check
        early_exit: DF.Check
        employee: DF.Link | None
        employee_name: DF.Data | None
        justification: DF.SmallText | None
        justification_date: DF.Datetime | None
        late_entry: DF.Check
        scheduled_in_time: DF.Time | None
        scheduled_out_time: DF.Time | None
        shift: DF.Link | None
        state: DF.Literal["Draft", "Pending Justification", "Pending Approval", "Approved", "Rejected", "Escalated", "Closed"]
        warning_date: DF.Date | None
        warning_type: DF.Literal["Late Entry", "Early Exit", "Absent", "Late Entry and Early Exit", "Custom"]
    # end: auto-generated types

    pass

    def validate(self):
        if self.is_new():
            self.send_employee_notification()

        user = frappe.session.user

        emp = frappe.db.get_value("Employee", {"user_id": user}, "name")

        if self.state == "Pending Approval" and self.has_value_changed("state"):
            if emp != self.employee:
                frappe.throw("Only the employee can submit justification")


    def send_employee_notification(self):
        message = None
        if not self.is_new():
            message = f"your justification was {self.state}"
        user = frappe.db.get_value("Employee", self.employee, "user_id")

        if user:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": message or f"You have received a warning.",
                "for_user": user,
                "type": "Alert",
                "document_type": self.doctype,
                "document_name": self.name
            }).insert(ignore_permissions=True)

            # frappe.sendmail(recipients=[user], sender= user, subject="No Subject", message="No Message", as_markdown=False, template=None, args=None, **kwargs)

    def send_approval_notification(self):
        user = self.approver


        if user:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"{self.employee_name} Submitted a justification regarding...",
                "for_user": user,
                "type": "Alert",
                "document_type": self.doctype,
                "document_name": self.name
            }).insert(ignore_permissions=True)

    def on_update(self):
        if not self.has_value_changed("state"):
            return
        if self.state == "Pending Approval":
            self.send_approval_notification()

        if self.state in ("Approved", "Rejected"):
            self.send_employee_notification()