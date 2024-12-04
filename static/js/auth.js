// Ensure the script runs after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const signInForm = document.getElementById("sign-in-form");

    // Ensure the form exists before adding an event listener
    if (!signInForm) {
        console.error("Sign-in form not found in the DOM.");
        return;
    }

    signInForm.addEventListener("submit", async (e) => {
        e.preventDefault(); // Prevent the default form submission

        // Get the input fields
        const emailInput = document.getElementById("email");
        const passwordInput = document.getElementById("password");

        // Check if the inputs exist
        if (!emailInput || !passwordInput) {
            console.error("Email or Password input field not found in the DOM.");
            return;
        }

        // Retrieve the values from the input fields
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        // Validate the input fields
        if (!email || !password) {
            alert("Please fill out both the email and password fields.");
            return;
        }

        try {
            // Send a POST request to the backend for authentication
            const response = await fetch("/user/sign_in", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.message); // Sign-in successful
                // Optional: Redirect to a dashboard or another page
                // window.location.href = "/dashboard";
            } else {
                alert(data.message); // Show error message from the backend
            }
        } catch (error) {
            console.error("Error signing in:", error);
            alert("An error occurred while trying to sign in. Please try again.");
        }
    });
});
