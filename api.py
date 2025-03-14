import frappe
import json
from frappe.utils.response import build_response
from frappe import _

@frappe.whitelist()
def get_user_details(email=None):
    if not email:
        return {"error": "Email parameter is required."}

    try:
        user = frappe.get_doc("User", email)
        
        return {
            "full_name": user.full_name,
            "email": user.email,
            "role_profile_name": user.role_profile_name,
            "enabled": user.enabled
        }
    
    except frappe.DoesNotExistError:
        return {"error": "User not found."}
    
    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist()
def get_dashboard_data(role_profile_name=None, user_email=None):
    try:
        if role_profile_name == "Task-Boss":
            tasks = frappe.db.get_list(
                "TaskLists",
                filters={},
                fields=["assigned_project", "task_name", "task_type", "assigned_employee", "assigned_by", "task_date", "task_due_date", "task_department", "task_status"]
            )
        elif role_profile_name == "Task-Lead":
            user_doc = frappe.get_doc("TaskEmployee", {"email": user_email})
            user_full_name = user_doc.full_name
            user_department_name = user_doc.department_name
            tasks = frappe.db.get_list(
                "TaskLists",
                filters={"task_department": user_department_name, "assigned_employee": ["!=", user_full_name]},
                fields=["assigned_project", "task_name", "task_type", "assigned_employee", "assigned_by", "task_date", "task_due_date", "task_department", "task_status"]
            )
        else:
            user_doc = frappe.get_doc("TaskEmployee", {"email": user_email})
            user_full_name = user_doc.full_name
            user_department_name = user_doc.department_name
            tasks = frappe.db.get_list(
                "TaskLists",
                filters={"assigned_employee": user_full_name},
                fields=["assigned_project", "task_name", "task_type", "assigned_employee", "assigned_by", "task_date", "task_due_date", "task_department", "task_status"]
            )
        return {"success": True, "tasks": tasks}
    except Exception as e:
        frappe.log_error(f"Dashboard Data Error: {str(e)}", "get_dashboard_data")
        return {"success": False, "error": str(e)}
    
@frappe.whitelist()
def get_lead_dashboard_data(role_profile_name=None, user_email=None):
    try:
        if role_profile_name == "Task-Boss":
            leadtasks = None
        elif role_profile_name == "Task-Lead":
            user_doc = frappe.get_doc("TaskEmployee", {"email": user_email})
            user_full_name = user_doc.full_name
            user_department_name = user_doc.department_name
            leadtasks =  frappe.db.get_list(
                "TaskLists",
                filters={"task_department": user_department_name, "assigned_employee": user_full_name},
                fields=["assigned_project", "task_name", "task_type", "assigned_employee", "assigned_by", "task_date", "task_due_date", "task_department", "task_status"]
            )
        else:
            user_doc = frappe.get_doc("TaskEmployee", {"email": user_email})
            user_full_name = user_doc.full_name
            user_department_name = user_doc.department_name
            leadtasks = None
        return {"success": True, "leadtasks": leadtasks}
    except Exception as e:
        frappe.log_error(f"Dashboard Data Error: {str(e)}", "get_dashboard_data")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_project_list():
    user = frappe.session.user
    user_full_name = frappe.get_value("TaskEmployee", {"email": user}, "full_name")
    user_role = frappe.get_value("TaskEmployee", {"email": user}, "department_post")
    filters = {}
    if user_role == "Employee":
        project_names = frappe.get_all(
            "TaskLists",
            filters={"assigned_employee": user_full_name},
            distinct=True,
            pluck="assigned_project"
        )
        if not project_names:
            return {"success": True, "projects": []}
        filters["name"] = ["in", project_names]
    elif user_role == "Lead":
        department_name = frappe.get_value("TaskEmployee", {"email": user}, "department_name")
        filters["assigned_department"] = department_name
    projects = frappe.get_all(
        "TaskProject",
        filters=filters,
        fields=["name as project_id", "project_name", "start_date", "end_date", "project_status", "assigned_department", "project_description"],
    )
    project_list = []
    for project in projects:
        task_count = frappe.db.count("TaskLists", {"assigned_project": project["project_id"]})
        pending_tasks = frappe.db.count("TaskLists", {"assigned_project": project["project_id"], "task_status": "Pending"})
        completed_tasks = frappe.db.count("TaskLists", {"assigned_project": project["project_id"], "task_status": "Completed"})
        assigned_employees = frappe.get_all(
            "TaskLists",
            filters={"assigned_project": project["project_name"]},
            fields=["assigned_employee"]
        )
        assigned_employee_names = list(set(emp["assigned_employee"] for emp in assigned_employees))
        project_list.append({
            "project_id": project["project_id"],
            "project_name": project["project_name"],
            "start_time": project["start_date"],
            "due_date": project["end_date"],
            "project_status": project["project_status"],
            "task_count": task_count,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "department": project["assigned_department"],
            "assigned_employees": assigned_employee_names,
            "project_description": project["project_description"]
        })
    return {"success": True, "projects": project_list}

@frappe.whitelist()
def get_project_details(project_id):
    try:
        project_desc = frappe.get_doc("TaskProject", {"project_name": project_id})
        user_email = frappe.session.user
        user_doc = frappe.get_doc("TaskEmployee", {"email": user_email})
        user_full_name = user_doc.full_name
        user_role = frappe.get_value("TaskEmployee", {"email": user_email}, "department_post")

        if user_role == "Lead":
            tasks = frappe.get_all(
                "TaskLists",
                filters={"assigned_project": project_id},
                fields=["assigned_project", "task_name", "task_type", "assigned_employee", "assigned_by", "task_date", "task_due_date", "task_department", "task_status"]
            )
        elif user_role == "Employee":
            tasks = frappe.get_all(
                "TaskLists",
                filters={"assigned_project": project_id, "assigned_employee": user_full_name},
                fields=["assigned_project", "task_name", "task_type", "assigned_employee", "assigned_by", "task_date", "task_due_date", "task_department", "task_status"]
            )
        else:
            tasks = []
        return {
            "success": True,
            "project_name": project_desc.project_name,
            "task_count": len(tasks),
            "pending_tasks": sum(1 for task in tasks if task["task_status"] == "Pending"),
            "completed_tasks": sum(1 for task in tasks if task["task_status"] == "Completed"),
            "tasks": tasks
        }
    except frappe.DoesNotExistError:
        return {"success": False, "error": "Project not found"}

@frappe.whitelist()
def get_task_details(task_id):
    try:
        task = frappe.get_doc("TaskLists", {"task_name": task_id})
        return {
            "success": True,
            "task_name": task.task_name,
            "task_type": task.task_type,
            "task_date": task.task_date,
            "task_assigned_by": task.assigned_by,
            "assigned_project": task.assigned_project,
            "task_description": task.task_description,
            "task_due_date": task.task_due_date,
            "task_assigned": task.assigned_employee,
            "task_department": task.task_department,
            "task_status": task.task_status,
            "task_remarks": task.task_remarks,
            "task_employee_description": task.task_employee_description,
            "task_employee_status": task.task_employee_status
        }
    except frappe.DoesNotExistError:
        return {"success": False, "error": "Task not found"}
    
@frappe.whitelist()   
def get_task_details_each_employee(each_employee):
    try:
        task = frappe.get_doc("TaskLists", {"assigned_employee": each_employee})
        return {
            "success": True,
            "task_name": task.task_name,
            "task_description": task.task_description,
            "task_due_date": task.task_due_date,
            "task_assigned": task.assigned_employee,
            "task_department": task.task_department,
            "task_status": task.task_status
        }
    except frappe.DoesNotExistError:
        return {"success": False, "error": "Task not found"}
    

@frappe.whitelist()
def get_all_employees():
    try:
        user = frappe.session.user
        user_details = frappe.get_value(
            "TaskEmployee", {"email": user}, ["department_post", "department_name"], as_dict=True
        )
        if not user_details:
            return {"message": "User not found"}
        frappe.logger().info(f"User Details: {user_details}")
        role = user_details.get("department_post")
        department = user_details.get("department_name")
        if role == "Head":
            employees = frappe.get_all(
                "TaskEmployee",
                fields=["full_name", "email", "department_name", "department_post"]
            )
        elif role == "Lead":
            employees = frappe.get_all(
                "TaskEmployee",
                filters={"department_name": department},
                fields=["full_name", "email", "department_name", "department_post"]
            )
        else:
            frappe.throw("You do not have permission to access employee details", frappe.PermissionError)
        return {"message": employees}
    except frappe.DoesNotExistError:
        return {"success": False, "error": "Data not found"}

@frappe.whitelist()
def get_employees():
    user_roles = frappe.get_roles(frappe.session.user)
    if "Task-Lead" not in user_roles and "Task-Boss" not in user_roles:
        frappe.throw(_("Access Denied"), frappe.PermissionError)
    employees = frappe.get_all("TaskEmployee", filters={"department_post": "Employee"}, fields=["name", "full_name"])
    return employees

@frappe.whitelist()
def create_task(task_name, task_description, task_due_date, assigned_employee, assigned_project, task_department, task_status):
    user_roles = frappe.get_roles(frappe.session.user)
    user = frappe.get_doc("User", frappe.session.user)
    if "Task-Lead" not in user_roles and "Task-Boss" not in user_roles:
        frappe.throw(_("Access Denied"), frappe.PermissionError)
    if not task_name.strip() or not task_description.strip() or not task_due_date:
        frappe.throw(_("Task Name, Description, and Due Date are required."))
    if task_due_date < frappe.utils.today():
        frappe.throw(_("Due Date cannot be in the past."))

    task_date = frappe.utils.today()

    task_completion_date = frappe.utils.today() if task_status == "Completed" else ""

    task = frappe.get_doc({
        "doctype": "TaskLists",
        "task_name": task_name.strip(),
        "task_description": task_description.strip(),
        "task_due_date": task_due_date,
        "task_date": task_date,
        "task_completion_date": task_completion_date,
        "assigned_employee": assigned_employee,
        "assigned_project": assigned_project,
        "task_department": task_department,
        "task_status": task_status,
        "assigned_by": user.full_name
    })

    task.insert()
    frappe.db.commit()

    return {"message": "Task Created Successfully", "task_name": task.name}


@frappe.whitelist()
def get_task_details_for_update(task_name):
    
    task = frappe.db.get_value("TaskLists", {"task_name": task_name}, "name")

    if not task:
        frappe.logger().error(f"Task '{task_name}' not found in the database.")
        frappe.throw(_("Task not found"))

    task_doc = frappe.get_doc("TaskLists", task)
    return task_doc.as_dict()


@frappe.whitelist()
def update_task(task_name, task_description, task_due_date, task_status):
    user_roles = frappe.get_roles(frappe.session.user)
    if "Task-Lead" not in user_roles and "Task-Boss" not in user_roles:
        frappe.throw(_("Access Denied"), frappe.PermissionError)
    task_id = frappe.db.get_value("TaskLists", {"task_name": task_name}, "name")
    if not task_id:
        frappe.throw(_("Task not found"))
    task = frappe.get_doc("TaskLists", task_id)
    if not task_description.strip() or not task_due_date:
        frappe.throw(_("Task Description and Due Date are required."))
    if task_due_date < frappe.utils.today():
        frappe.throw(_("Due Date cannot be in the past."))
    task.task_description = task_description.strip()
    task.task_due_date = task_due_date
    task.task_status = task_status
    if task_status == "Completed" and not task.task_completion_date:
        task.task_completion_date = frappe.utils.today()
    task.save()
    frappe.db.commit()
    return {"message": "Task Updated Successfully"}

@frappe.whitelist()
def delete_task(task_name):
    user_roles = frappe.get_roles(frappe.session.user)

    if "Task-Lead" not in user_roles and "Task-Boss" not in user_roles:
        frappe.throw(_("Access Denied"), frappe.PermissionError)

    task_id = frappe.db.get_value("TaskLists", {"task_name": task_name}, "name")

    if not task_id:
        frappe.throw(_("Task not found"))

    frappe.delete_doc("TaskLists", task_id, force=True)
    frappe.db.commit()

    return {"message": f"Task '{task_name}' deleted successfully"}

@frappe.whitelist()
def get_task_details_for_update(task_name):
    
    task = frappe.db.get_value("TaskLists", {"task_name": task_name}, "name")

    if not task:
        frappe.logger().error(f"Task '{task_name}' not found in the database.")
        frappe.throw(_("Task not found"))

    task_doc = frappe.get_doc("TaskLists", task)
    return task_doc.as_dict()

@frappe.whitelist()
def get_task_employee_status_options():
    """Fetch allowed employee status options."""
    return ["Pending", "Completed"]

@frappe.whitelist()
def update_employee_status(task_id, task_employee_description, task_employee_status):
    """Update employee feedback and status for a specific task."""

    user = frappe.session.user

    # 🔍 Debugging: Log the received task_id
    frappe.logger().info(f"Received task_id: {task_id}")

    # 🔍 Check if task exists using both `name` and `task_name`
    if not frappe.db.exists("TaskLists", {"name": task_id}) and not frappe.db.exists("TaskLists", {"task_name": task_id}):
        frappe.logger().error(f"Task not found in database: {task_id}")
        frappe.throw(_("Task not found"))

    # Get the task document
    task_doc = frappe.get_doc("TaskLists", {"name": task_id} if frappe.db.exists("TaskLists", {"name": task_id}) else {"task_name": task_id})

    # # Ensure the user is allowed to update this task
    # if task_doc.assigned_employee != user:
    #     frappe.throw(_("You are not authorized to update this task."))

    # Update the fields
    task_doc.task_employee_description = task_employee_description
    task_doc.task_employee_status = task_employee_status

    # # If status is "Completed", set task completion date
    # if task_employee_status == "Task Finished" and not task_doc.task_completion_date:
    #     task_doc.task_completion_date = frappe.utils.today()

    task_doc.save()
    frappe.db.commit()

    return {"message": "Employee status updated successfully"}
