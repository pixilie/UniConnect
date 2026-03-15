const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE_URL = isLocal ? "http://localhost:8000/api" : "https://uniconnect.pixilie.net/api";

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
        console.log(err);
        errorMessage = err;
        return false;
    }
}

document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    let fullName = document.getElementById("fullname").value.trim();
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    let names = fullName.split(" ");
    let firstName = names[0];
    names.shift();
    let lastName = names.join(" ") || "";
    let message = document.getElementById("message");
    let success = await register(firstName, lastName, email, password);

    if (success) {
        message.style.color = "green";
        message.innerText = "Registration Successful!";
        window.location.href = "login.html";
    }
    else {
        message.style.color = "red";
        message.innerText = errorMessage;
    }
});
