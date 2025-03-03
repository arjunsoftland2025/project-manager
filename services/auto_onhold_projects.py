import frappe

def update_tasks_for_on_hold_projects():
    # Get all projects where status is "On Hold"
    on_hold_projects = frappe.get_all("ProjectDetails", filters={"project_status": "On Hold"}, pluck="name")

    if on_hold_projects:
        # Update related tasks to "On Hold"
        frappe.db.set_value(
            "TaskDetails",
            {"assigned_project": ["in", on_hold_projects]},
            "task_status",
            "On Hold",
            update_modified=True
        )
        frappe.db.commit()
        frappe.logger().info(f"Updated tasks to 'On Hold' for projects: {on_hold_projects}")

    # Get projects that are "Live" (reopen tasks if needed)
    live_projects = frappe.get_all("ProjectDetails", filters={"project_status": "Live"}, pluck="name")

    if live_projects:
        # Reopen tasks that were previously "On Hold"
        frappe.db.set_value(
            "TaskDetails",
            {
                "assigned_project": ["in", live_projects],
                "task_status": "On Hold"
            },
            "task_status",
            "Pending",
            update_modified=True
        )
        frappe.db.commit()
        frappe.logger().info(f"Reopened tasks for live projects: {live_projects}")
