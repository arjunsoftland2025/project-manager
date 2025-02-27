import frappe
from datetime import datetime

def before_save_task(doc, method):
    # Ensure task_date is set
    if not doc.task_date:
        doc.task_date = datetime.today().date()  # Set today's date if empty

    # Format task date to DD-MM-YY
    formatted_date = doc.task_date.strftime('%d-%m-%y')

    # Format employee name (lowercase + underscores)
    employee_name = doc.assigned_employee.lower().replace(" ", "_")

    # Count existing tasks for the same employee and date
    task_count = frappe.db.count('TaskDetails', {
        'assigned_employee': doc.assigned_employee,
        'task_date': doc.task_date  # Ensure task_date is stored as a Date field
    })

    # Generate new task number
    task_number = f"task{task_count + 1:03d}"  # task001, task002, etc.

    # Set final task name
    doc.custom_task_name = f"{employee_name}/{formatted_date}/{task_number}"
