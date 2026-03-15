const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE_URL = isLocal ? "http://localhost:8000/api" : "https://uniconnect.pixilie.net/api";

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
