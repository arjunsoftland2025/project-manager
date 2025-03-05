import frappe

def update_tasks_for_on_hold_projects():
    try:
        on_hold_projects = frappe.get_all("TaskProject", filters={"project_status": "On Hold"}, pluck="name")
        if on_hold_projects:
            frappe.db.set_value(
                "TaskLists",
                {"assigned_project": ["in", on_hold_projects]},
                "task_status",
                "On Hold",
                update_modified=True
            )
            frappe.logger().info(f"Updated tasks to 'On Hold' for projects: {on_hold_projects}")
        else:
            frappe.logger().info("No 'On Hold' projects found.")
    except frappe.DoesNotExistError as e:
        frappe.log_error(f"Project or task not found: {e}")
    except frappe.ValidationError as e:
        frappe.log_error(f"Validation error while updating tasks: {e}")
    except Exception as e:
        frappe.log_error(f"Unexpected error fetching 'On Hold' projects: {e}")
        return
    
    try:
        live_projects = frappe.get_all("TaskProject", filters={"project_status": "Live"}, pluck="name")
        if live_projects:
            frappe.db.set_value(
                "TaskLists",
                {"assigned_project": ["in", live_projects]},
                "task_status",
                "Pending",
                update_modified=True
            )
            frappe.logger().info(f"Reopened tasks for live projects: {live_projects}")
        else:
            frappe.logger().info("No 'Live' projects found.")
    except frappe.DoesNotExistError as e:
        frappe.log_error(f"Project or task not found: {e}")
    except frappe.ValidationError as e:
        frappe.log_error(f"Validation error while reopening tasks: {e}")
    except Exception as e:
        frappe.log_error(f"Unexpected error fetching 'Live' projects: {e}")
        return
    
    try:
        # Commit changes after all operations
        frappe.db.commit()
        frappe.logger().info("Database changes committed successfully.")
    except Exception as e:
        frappe.log_error(f"Error committing changes to the database: {e}")
