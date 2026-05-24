let error = 'Invalid email or password';

async function login(username, password) {
    const params = new URLSearchParams();
    params.append('grant_type', 'password');
    params.append('username', username);
    params.append('password', password);
    error = 'Invalid email or password';

    try {
        const res = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: params,
        });

        if (!res.ok) return false;

        const data = await res.json();
        localStorage.setItem('token', data.access_token);

        return true;
    } catch (err) {
        let message = document.getElementById('message');
        message.style.color = 'red';
        error = err.message || 'Network error';
        message.innerText = error;
        return false;
    }
}

async function getUserProfile(token) {
    try {
        const res = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!res.ok) return null;

        return await res.json();
    } catch (err) {
        let message = document.getElementById('message');
        message.style.color = 'red';
        message.innerText = err;

        return null;
    }
}

document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;
    let message = document.getElementById('message');
    let loginSuccess = await login(email, password);

    if (loginSuccess) {
        message.style.color = 'green';
        message.innerText = 'Login Successful! Checking account status...';

        const token = localStorage.getItem('token');
        const userData = await getUserProfile(token);

        AppState.userProfile = userData;

        if (userData && userData.groups && userData.groups.length > 0) {
            const defaultGroup = userData.groups[0];

            AppState.currentGroupId = defaultGroup.id;
            AppState.currentGroupName = defaultGroup.name || '';

            localStorage.setItem('groupID', defaultGroup.id);
            window.location.href = 'chat.html';
        } else {
            window.location.href = 'no_group.html';
        }
    } else {
        message.style.color = 'red';
        message.innerText = error;
    }
});

checkLoginStatus();
