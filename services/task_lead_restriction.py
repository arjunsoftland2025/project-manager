# import frappe

# def set_user_permissions(user):
#     """Automatically restrict Task-Lead to their department."""
#     # Get the user's department
#     department_name = frappe.get_value("EmployeeDetails", {"user": user}, "department_name")

#     if department_name:
#         # Check if permission already exists
#         existing_permission = frappe.get_all(
#             "User Permission",
#             filters={
#                 "user": user,
#                 "allow": "EmployeeDetails",
#                 "for_value": department_name
#             }
#         )

#         if not existing_permission:
#             # Assign department_name as a User Permission
#             user_permission = frappe.get_doc({
#                 "doctype": "User Permission",
#                 "user": user,
#                 "allow": "EmployeeDetails",
#                 "for_value": department_name,
#                 "apply_to_all_doctypes": 0
#             })
#             user_permission.insert(ignore_permissions=True)

#             frappe.db.commit()


import frappe

def set_user_permissions(doc, method):
    # Check if the employee is a Task-Lead
    if doc.department_post == "Lead":
        # Create or update User Permission for the Task-Lead
        user_permission = frappe.get_doc({
            "doctype": "User Permission",
            "user": doc.email,  # Assuming email is the user ID
            "allow": "Department",
            "for_value": doc.department_name,
            "apply_to_all_doctypes": 0
        })

        # Add specific DocTypes to restrict
        user_permission.append("applicable_for", {
            "applicable_for_doctype": "EmployeeDetails"
        })
        user_permission.append("applicable_for", {
            "applicable_for_doctype": "ProjectDetails"
        })
        user_permission.append("applicable_for", {
            "applicable_for_doctype": "TaskDetails"
        })

        user_permission.save(ignore_permissions=True)
