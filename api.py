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

    user_role = frappe.get_value("TaskEmployee", {"email": user}, "department_post")

    filters = {}

    if user_role == "Task-Lead":
        department_name = frappe.get_value("TaskEmployee", "department_name")
        filters["department"] = department_name
    elif user_role == "Task-Employee":
        filters["assigned_employee"] = user
    projects = frappe.get_all(
        "TaskProject",
        filters=filters,
        fields=["name as project_id", "project_name"],
    )

    project_list = []

    for project in projects:
        task_count = frappe.db.count("TaskLists", {"assigned_project": project["project_id"]})
        pending_tasks = frappe.db.count("TaskLists", {"assigned_project": project["project_id"], "task_status": "Pending"})
        
        project_list.append({
            "project_id": project["project_id"],
            "project_name": project["project_name"],
            "task_count": task_count,
            "pending_tasks": pending_tasks
        })

    return {"success": True, "projects": project_list}

@frappe.whitelist()
def get_project_details(project_id):
    project_desc = frappe.get_doc("TaskProject", {"project_name": project_id})

    tasks = frappe.get_all(
        "TaskLists",
        filters={"assigned_project": project_id},
        fields=["task_name", "task_description", "task_status"]
    )

    return {
        "success": True,
        "project_name": project_desc.project_name,
        "task_count": len(tasks),
        "pending_tasks": sum(1 for task in tasks if task["task_status"] == "Pending"),
        "tasks": tasks
    }

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
            "task_status": task.task_status
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

