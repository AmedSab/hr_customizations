// Copyright (c) 2026, Ahmed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Warning", {
    async refresh(frm) {
        let user_emp = await frappe.db.get_value(
            "Employee",
            { user_id: frappe.session.user },
            "name"
        );

        if (frm.doc.state === "Pending Justification" && user_emp.message.name === frm.doc.employee) {
            frm.add_custom_button("Submit Justification", () => {
                frm.set_value("state", "Pending Approval");
                frm.set_value("justification_date", frappe.datetime.now_datetime());
                frappe.show_alert('Submitted Justification');
                frm.save();
                frm.set_df_property("justification", "read_only", 1);
            });
        }

        if (frm.doc.state === "Pending Approval" && frm.doc.approver === frappe.session.user) {
            frm.add_custom_button("Submit Approval", () => {
                frm.set_value("state", frm.doc.approval_decision);
                frm.set_value("approval_date", frappe.datetime.now_datetime());

                frm.save("Submit").then(() => {
                    // This ensures the document is submitted after the save is successful
                    frappe.show_alert({
                        message: __("Document Approved and Submitted"),
                        indicator: 'green'
                    });
                });
            });
        }
    }
});
