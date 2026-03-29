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

    
    def deduct_leave(self):
        if not self.employee or not self.leave_type_for_deduction:
            frappe.throw("Employee and Leave Type are required")

        leave_date = get_next_valid_day(self.employee, nowdate())

        
        leave = frappe.get_doc({
        "doctype": "Leave Application",
        "employee": self.employee,
        "leave_type": self.leave_type_for_deduction,
        "from_date":leave_date,
        "to_date": leave_date,
        "description": f"Auto deduction from escalation {self.name}"
    })

        leave.insert(ignore_permissions=True)
        leave.submit()    

        # allocation = frappe.get_all("Leave Allocation", 
        #                 filters={'leave_type': ['=', self.leave_type_for_deduction], 'docstatus': ['=', 1]
        #                          , 'employee': ['=', self.employee]
        #                          }, 
        #                 fields=["name", "employee", "new_leaves_allocated", "total_leaves_allocated"],
        #                 limit=1
        #                 )
        
        # if allocation:
        #     frappe.db.set_value(
        #         "Leave Allocation",
        #         allocation[0].name,
        #         "total_leaves_allocated",
        #         allocation[0].total_leaves_allocated - 1
        #     )

        frappe.logger().info(f"Leave deducted for {self.employee}")


        def get_next_valid_day(self, employee, date):
            holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")

            while True:
                is_holiday = frappe.db.exists("Holiday", {
                    "parent": holiday_list,
                    "holiday_date": date
                })

                leave_exists = frappe.db.exists("Leave Application", {
                    "employee": employee,
                    "leave_type": self.leave_type_for_deduction,
                    "docstatus": 1,
                    "from_date": ["<=", date],
                    "to_date": [">=", date]
                })

                if not is_holiday and not leave_exists:
                    return date

                date = add_days(date, 1)

