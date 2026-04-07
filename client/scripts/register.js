let errorMessage = "Registration failed. Email might already exist.";

async function register(firstName, lastName, email, password) {
    errorMessage = "Registration failed. Email might already exist.";

    try {
        const res = await fetch(`${API_BASE_URL}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password
            })
        });

        if (!res.ok) return false;
        return true;
    } catch (err) {
        errorMessage = err;
        return false;
    }
}

document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    let firstname = document.getElementById("firstname").value.trim();
    let lastname = document.getElementById("lastname").value.trim();
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    let message = document.getElementById("message");
    let success = await register(firstname, lastname, email, password);

    if (success) {
        message.style.color = "green";
        message.innerText = "Registration Successful!";
        window.location.href = "login.html";
    } else {
        message.style.color = "red";
        message.innerText = errorMessage;
    }
});

checkLoginStatus();
