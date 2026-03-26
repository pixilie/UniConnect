const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

const API_BASE_URL = isLocal ? "http://localhost:8000/api" : "https://uniconnect.pixilie.net/api";
const WS_BASE_URL = isLocal ? "ws://localhost:8000/ws" : "wss://uniconnect.pixilie.net/ws";

const AppState = {
    currentGroupId: localStorage.getItem("groupID") || null,
    currentGroupName: "",
    userProfile: null
};

function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

function goBackSafely() {
    const previousPage = document.referrer;

    if (previousPage && previousPage.includes(window.location.hostname) && !previousPage.includes("login.html")) {
        window.location.href = previousPage;
    } else if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = "unauthorized.html";
    }
}

async function adminOnly() {
    const token = localStorage.getItem("token");

    if (!token) {
        logout();
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

            if (userData.role !== "administrator") {
                goBackSafely();
            } else if (userData.groups && userData.groups.length < 0) {
                window.location.href = "no_group.html";
            }
        } else if (res.status === 401) {
            logout();
        } else {
            console.error("Error fetching status.");
            goBackSafely();
        }
    } catch (error) {
        goBackSafely();
        console.error("Network error:", error);
    }
}

async function requireAuth() {
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

        if (!res.ok) {
            logout();
        }

        const userData = await res.json();

        if (userData.groups && userData.groups.length < 0 && window.location.href != "no_group.html") {
            window.location.href = "no_group.html";
        }

    } catch (error) {
        console.error("Network error:", error);
    }
}

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
