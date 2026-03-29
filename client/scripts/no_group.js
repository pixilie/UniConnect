requireAuth();

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
            const error = await res.json();
            window.alert(`Error while getting status: ${error}`);
        }
    } catch (error) {
        console.error("Network error:", error);
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}
