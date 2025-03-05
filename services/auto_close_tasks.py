import frappe
from frappe.utils import today

def auto_close_expired_tasks():
    try:
        expired_projects = frappe.get_all(
            "TaskProject", 
            filters={"end_date": ["<", today()]}, 
            pluck="name"
        )
        
        if expired_projects:
            frappe.db.set_value(
                "TaskLists",
                {
                    "assigned_project": ["in", expired_projects],
                    "task_status": ["not in", ["Completed", "On Hold"]]
                },
                "task_status",
                "Closed",
                update_modified=True
            )
            frappe.logger().info(f"Auto-closed tasks for expired projects: {', '.join(expired_projects)}")
        else:
            frappe.logger().info("No expired projects found.")
    except frappe.DoesNotExistError as e:
        frappe.log_error(f"Project or task not found during expired task closure: {e}")
    except frappe.ValidationError as e:
        frappe.log_error(f"Validation error during expired task closure: {e}")
    except Exception as e:
        frappe.log_error(f"Error occurred while fetching expired projects or updating tasks: {e}")
        return

    try:
        active_projects = frappe.get_all(
            "TaskProject", 
            filters={"end_date": [">=", today()]}, 
            pluck="name"
        )
        
        if active_projects:
            frappe.db.set_value(
                "TaskLists",
                {
                    "assigned_project": ["in", active_projects],
                    "task_status": "Closed"
                },
                "task_status",
                "Pending",
                update_modified=True
            )
            frappe.logger().info(f"Reopened tasks for active projects: {', '.join(active_projects)}")
        else:
            frappe.logger().info("No active projects found.")
    except frappe.DoesNotExistError as e:
        frappe.log_error(f"Project or task not found during task reopening: {e}")
    except frappe.ValidationError as e:
        frappe.log_error(f"Validation error during task reopening: {e}")
    except Exception as e:
        frappe.log_error(f"Error occurred while fetching active projects or updating tasks: {e}")
        return

    try:
        active_tasks = frappe.get_all(
            "TaskLists",
            filters={
                "due_date": [">=", today()],
                "task_status": "Closed"
            },
            pluck="name"
        )
        
        if active_tasks:
            # Update all tasks in bulk instead of in a loop
            for task in active_tasks:
                frappe.db.set_value("TaskLists", task, "task_status", "Pending", update_modified=True)
            frappe.logger().info(f"Reopened {len(active_tasks)} standalone tasks with extended due date.")
        else:
            frappe.logger().info("No standalone tasks found with extended due date.")
    except frappe.DoesNotExistError as e:
        frappe.log_error(f"Task not found during reopening standalone tasks: {e}")
    except frappe.ValidationError as e:
        frappe.log_error(f"Validation error during reopening standalone tasks: {e}")
    except Exception as e:
        frappe.log_error(f"Error occurred while fetching active tasks or updating task statuses: {e}")
        return

    try:
        # Commit changes after all operations are complete
        frappe.db.commit()
        frappe.logger().info("Database changes committed successfully.")
    except Exception as e:
        frappe.log_error(f"Error occurred during database commit: {e}")
