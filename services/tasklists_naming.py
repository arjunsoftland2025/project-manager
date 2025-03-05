import frappe
from datetime import datetime

def before_insert_task(doc, method):
    try:
        # Ensure task_date is set
        if not doc.task_date:
            doc.task_date = datetime.today().date()  # Set today's date if empty

        # Format task date to DD-MM-YY
        formatted_date = doc.task_date.strftime('%d-%m-%y')

        # Ensure assigned_employee is provided and valid
        if not doc.assigned_employee:
            frappe.throw("Assigned employee is required to create a task.")
        
        # Format employee name (lowercase + underscores)
        employee_name = doc.assigned_employee.lower().replace(" ", "_")

        # Count existing tasks for the same employee and date
        task_count = frappe.db.count('TaskLists', {
            'assigned_employee': doc.assigned_employee,
            'task_date': doc.task_date  # Ensure task_date is stored as a Date field
        })

        # Generate new task number (task001, task002, etc.)
        task_number = f"task{task_count + 1:03d}"

        # Set final custom task name
        doc.custom_task_name = f"{employee_name}/{formatted_date}/{task_number}"

    except Exception as e:
        # Log error and raise a user-friendly error message
        frappe.log_error(f"Error in task naming: {str(e)}")
        frappe.throw("An error occurred while generating the custom task name.")
