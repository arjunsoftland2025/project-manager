const API_URL = "/api/method";

// Fetch current user email
async function getCurrentUserEmail() {
    const response = await fetch(API_URL + "/frappe.auth.get_logged_user", {
        method: "GET",
        credentials: "include"
    });
    if (!response.ok) throw new Error("Failed to fetch user email");
    const data = await response.json();
    return data.message;  // This returns the logged-in user's email.
}

// Fetch user role based on email
async function getUserRole() {
    try {
        const userEmail = await getCurrentUserEmail();  // Get user email first
        const response = await fetch(API_URL + "/frappe.client.get_value", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                doctype: "User",
                filters: { "email": userEmail },
                fieldname: "role_profile_name"
            })
        });
        if (!response.ok) throw new Error("Failed to fetch role");
        const data = await response.json();
        return data.message.role_profile_name;  // This returns the role name
    } catch (error) {
        console.error("Error fetching user role:", error);
        return null;
    }
}

// Check role permissions and redirect if unauthorized
async function checkAccess(requiredRole, redirectPage = "404.html") {
    try {
        const userRole = await getUserRole();
        if (userRole !== requiredRole) {
            window.location.href = redirectPage;
        }
    } catch (error) {
        console.error("Access check failed:", error);
        window.location.href = redirectPage;
    }
}
