import frappe
from frappe.utils import today

def before_save_task(doc, method):
    if doc.get_doc_before_save():  # Ensure this is an update, not a new doc
        previous_status = doc.get_doc_before_save().task_status

        if previous_status in ["Closed", "Completed"]:
            frappe.throw("This task is already closed or completed and cannot be modified.")

    if doc.task_status == "Completed" and not doc.task_completion_date:
        doc.task_completion_date = today()

