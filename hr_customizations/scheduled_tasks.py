import frappe
from datetime import date, timedelta
from frappe.utils import add_to_date


first_day_of_month = date.today().replace(day=1)
yesterday = date.today() - timedelta(days=1)

ATTENDANCE_DATE_FROM = first_day_of_month

def generate_attendance_warnings():
    settings = frappe.get_single('HR Customizations Settings')

    attendances = frappe.get_all("Attendance", 
                                filters={'attendance_date': ['>=', ATTENDANCE_DATE_FROM], "status": ["in", ["Absent", "Present"]]}, 
                                fields=["name", "employee", "employee_name", "attendance_date", "company", "shift", "status"]
                                )

    for att in attendances:
        employee = frappe.get_doc("Employee", att.employee)
        shift = frappe.db.get_value("Shift Type", att.shift, ["start_time", "end_time"], as_dict=1)

        late_entry = False
        early_exit = False
        absent = False

        if not shift or not shift.start_time or not shift.end_time:
            continue

        scheduled_in = shift.start_time
        scheduled_out = shift.end_time

        max_in_time = scheduled_in + timedelta(minutes=settings.late_entry_threshold_minutes)
        min_out_time = scheduled_out - timedelta(minutes=settings.early_exit_threshold_minutes)

        actual_in_time = frappe.db.get_value("Attendance", att.name, "in_time")
        actual_out_time = frappe.db.get_value("Attendance", att.name, "out_time")

        absent = True if att.status == "Absent" else False

        if not actual_in_time or not actual_out_time:
            absent = True
        else:
            is_late = actual_in_time > max_in_time
            is_early = actual_out_time < min_out_time
            if is_early:
                early_exit = True
            elif is_late:
                late_entry = True
        
        if late_entry or early_exit or absent:

            exists = frappe.db.exists(
                "Attendance Warning",
                {
                    "employee": att.employee,
                    "attendance": att.name,
                    "warning_date": att.attendance_date,
                },
            )

            if exists:
                continue

            warning = frappe.get_doc({
                "doctype": "Attendance Warning",  
                "employee": att.employee,
                "employee_name": att.employee_name,
                "warning_date": att.attendance_date,
                "attendance": att.name,
                "company": att.company,
                "late_entry": late_entry,
                "early_exit": early_exit,
                "absent": absent,
                "shift": att.shift,
                "state": "Pending Justification",
                "approver": employee.shift_request_approver,
            })

            print("Warning Created")

            warning.insert()


def evaluate_attendance_escalations():
    warnings = frappe.get_all("Attendance Warning", 
                        filters={'warning_date': ['>=', first_day_of_month], 'docstatus': ['=', 1]
                                 , 'state': ['=', 'Rejected']
                                 }, 
                        fields=["name", "employee", "employee_name", "warning_date", "company", "shift", "state"],
                        )

    hr_customization_settings = frappe.get_single('HR Customizations Settings')

    grouped_warnings = {}

    for w in warnings:
        grouped_warnings[w.employee] = grouped_warnings.get(w.employee, [])
        grouped_warnings[w.employee].append(w)


    for employee, emp_warnings in grouped_warnings.items():
        count = len(emp_warnings)
        if count >= hr_customization_settings.escalation_rejection_limit:
            exists = frappe.db.exists(
                "Attendance Escalation Action",
                {
                    "employee": employee,
                    "escalation_date": ['>=', first_day_of_month],
                },
            )

            if exists:
                continue

            for w in warnings:
                # Use set_value to skip the "Update After Submit" validation
                frappe.db.set_value("Attendance Warning", w.name, "state", "Escalated")
            
            frappe.db.commit()

            escalation = frappe.get_doc({
                "doctype": "Attendance Escalation Action",  
                "employee": employee,
                "rejection_warning_count": count,
                "escalation_date": date.today(),
            })
            user = frappe.db.get_value("Employee", employee, "user_id")

            if user:
                frappe.get_doc({
                    "doctype": "Notification Log",
                    "subject": "Attendance Escalation Action",
                    "email_content": f"Attendance Escalation Action.",
                    "for_user": user,
                    "type": "Alert",
                    "document_type": escalation.doctype,
                    "document_name": escalation.name
                }).insert(ignore_permissions=True)

            print("Escalation Created")

            escalation.insert()

    
    
