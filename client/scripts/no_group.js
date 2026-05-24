requireAuth();

async function reload() {
    const token = localStorage.getItem('token');

    if (!token) {
        logout();
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
        });

        if (res.ok) {
            const userData = await res.json();
            AppState.userProfile = userData;

            if (userData.groups && userData.groups.length > 0) {
                const defaultGroup = userData.groups[0];

                AppState.currentGroupId = defaultGroup.id;
                AppState.currentGroupName = defaultGroup.name || '';
                localStorage.setItem('groupID', defaultGroup.id);
                window.location.href = 'chat.html';
            } else {
                displayError("Status checked: Still no group assigned.");
            }
        } else if (res.status === 401) {
            logout();
        } else {
            const error = await res.json();
            displayError(`${error.detail}`);
        }
    } catch (error) {
        displayError(`Network error: ${displayError}`);
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('groupID');
    window.location.href = 'login.html';
}
