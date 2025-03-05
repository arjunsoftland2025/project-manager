import frappe
from frappe.utils import today

def before_save_task(doc, method):
    try:
        # Ensure we have a previous document (only relevant for updates, not new docs)
        if doc.get_doc_before_save():  
            previous_status = doc.get_doc_before_save().task_status

            # Prevent modification if task is closed or completed
            if previous_status in ["Closed", "Completed"]:
                frappe.throw("This task is already closed or completed and cannot be modified.")

        # Set task completion date when status is "Completed"
        if doc.task_status == "Completed" and not doc.task_completion_date:
            doc.task_completion_date = today()

        # Optionally, you could add additional validation for the task_completion_date here
        # For example, check if the completion date is not in the future
        if doc.task_status == "Completed" and doc.task_completion_date > today():
            frappe.throw("Task completion date cannot be in the future.")
        
    except frappe.ValidationError as ve:
        # Specific error handling for validation exceptions (optional)
        frappe.log_error(f"Validation error in before_save_task: {str(ve)}")
        frappe.throw(str(ve))
    except Exception as e:
        # Generic error handling for other unexpected issues
        frappe.log_error(f"Error in before_save_task: {str(e)}")
        frappe.throw("An unexpected error occurred while saving the task.")
