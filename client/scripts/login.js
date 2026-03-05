async function login(username, password) {
    const params = new URLSearchParams();
    params.append("grant_type", "password");
    params.append("username", username);
    params.append("password", password);

    try {
        const res = await fetch("http://localhost:3000/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: params
        });

        if (!res.ok) return false;

        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        return true;
    } catch (err) {
        return false;
    }
}
