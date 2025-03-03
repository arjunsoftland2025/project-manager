import frappe
from frappe.utils import today

def auto_close_expired_tasks():
    # Get all projects where end_date has passed
    expired_projects = frappe.get_all("ProjectDetails", filters={"end_date": ["<", today()]}, pluck="name")

    # Auto-close tasks (Exclude 'Completed' and 'On Hold' tasks)
    if expired_projects:
        frappe.db.set_value(
            "TaskDetails",
            {
                "assigned_project": ["in", expired_projects],
                "task_status": ["not in", ["Completed", "On Hold"]]
            },
            "task_status",
            "Closed",
            update_modified=True
        )
        frappe.db.commit()
        frappe.logger().info(f"Auto-closed tasks for expired projects: {expired_projects}")

    # Get projects with extended end_date (Reopen tasks)
    active_projects = frappe.get_all("ProjectDetails", filters={"end_date": [">=", today()]}, pluck="name")

    # Reopen tasks only if they were previously "Closed" (Exclude 'Completed' and 'On Hold' tasks)
    if active_projects:
        frappe.db.set_value(
            "TaskDetails",
            {
                "assigned_project": ["in", active_projects],
                "task_status": "Closed"
            },
            "task_status",
            "Pending",
            update_modified=True
        )
        frappe.db.commit()
        frappe.logger().info(f"Reopened tasks for extended projects: {active_projects}")

    # Reopen standalone tasks if due_date is extended (Exclude 'Completed' and 'On Hold' tasks)
    active_tasks = frappe.get_all(
        "TaskDetails",
        filters={
            "due_date": [">=", today()],
            "task_status": "Closed"
        },
        pluck="name"
    )

    if active_tasks:
        for task in active_tasks:
            frappe.db.set_value("TaskDetails", task, "task_status", "Pending", update_modified=True)
        frappe.db.commit()
        frappe.logger().info(f"Reopened standalone tasks with extended due_date: {active_tasks}")
