const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE_URL = isLocal ? "http://localhost:8000/api" : "https://uniconnect.pixilie.net/api";

async function login(username, password) {
    const params = new URLSearchParams();
    params.append("grant_type", "password");
    params.append("username", username);
    params.append("password", password);

    try {
        const res = await fetch(`${API_BASE_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: params
        });

        if (!res.ok) return false;

        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        return true;

    } catch (err) {
        console.log(err);
        return false;
    }
}

async function getUserProfile(token) {
    try {
        const res = await fetch(`${API_BASE_URL}/users/me`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) return null;
        return await res.json();
    } catch (err) {
        console.log(err);
        return null;
    }
}

document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;
    let message = document.getElementById("message");

    let loginSuccess = await login(email, password);

    if (loginSuccess) {
        message.style.color = "green";
        message.innerText = "Login Successful! Checking account status...";

        const token = localStorage.getItem("token");
        const userData = await getUserProfile(token);

        if (userData && userData.groups && userData.groups.length > 0) {
            window.location.href = "chat.html";
        } else {
            window.location.href = "no_group.html";
        }

    } else {
        message.style.color = "red";
        message.innerText = "Invalid email or password";
    }
});

async function checkLoginStatus() {
    const token = localStorage.getItem("token");

    if (!token) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/users/me`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        if (res.ok) {
            const userData = await res.json();

            if (userData.groups && userData.groups.length > 0) {
                window.location.href = "chat.html";
            } else {
                window.location.href = "no_group.html";
            }

        } else if (res.status === 401) {
            localStorage.removeItem("token");
        }
    } catch (error) {
        console.error(error);
    }
}

checkLoginStatus();
