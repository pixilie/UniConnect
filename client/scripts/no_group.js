const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE_URL = isLocal ? "http://localhost:8000/api" : "https://uniconnect.pixilie.net/api";

async function reload() {
    const token = localStorage.getItem("token");

    if (!token) {
        logout();
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
            }
        } else if (res.status === 401) {
            logout();
        } else {
            console.error("Error fetching status.");
        }
    } catch (error) {
        console.error("Network error:", error);
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}
