// Function to check user role and redirect if unauthorized
function checkUserRole(requiredRole, currentPage) {
    // Make a fetch call to get the user's role from the server
    fetch('/api/method/my_custom_app.get_user_role')  // Replace with your custom API endpoint
        .then(response => response.json())  // Parse the JSON response
        .then(data => {
            // Check if the response contains the role
            console.log(data.role_profile_name)
            if (data.role_profile_name) {
                let userRole = data.role_profile_name;

                // Define allowed pages for each role
                let rolePages = {
                    "Task-Boss": "project-boss-dashboard.html",
                    "Task-Lead": "project-lead-dashboard.html",
                    "Task-Employee": "project-employee-dashboard.html"
                };

                // If the user tries to access a restricted page, show error & redirect
                if (userRole !== requiredRole) {
                    alert("Access Denied! You are not allowed to view this dashboard.");
                    window.location.href = rolePages[userRole] || "/"; // Redirect to correct page
                }
            } else {
                alert("Unable to fetch user role.");
            }
        })
        .catch(error => {
            console.error("Error fetching user role:", error);
            alert("An error occurred while checking your role. Please try again.");
        });
}
