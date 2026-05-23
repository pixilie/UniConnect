const isLocal =
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const API_BASE_URL = isLocal ? 'http://localhost:8000/api' : 'https://uniconnect.pixilie.net/api';
const WS_BASE_URL = isLocal ? 'ws://localhost:8000/ws' : 'wss://uniconnect.pixilie.net/ws';

const errorDisplay = document.getElementById('errorDisplay');
const errorMessage = document.getElementById('errorDisplayMessage');
const errorCloseBtn = document.getElementById('errorDisplayCloseBtn');

let errorTimeout;

const AppState = {
    currentGroupId: localStorage.getItem('groupID') || null,
    currentGroupName: '',
    userProfile: null,
};

function logout() {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
}

function displayError(msg) {
    if (!errorDisplay || !errorMessage) {
        return window.alert(msg);
    }

    errorMessage.textContent = msg;
    errorDisplay.classList.add('show');

    clearTimeout(errorTimeout);
    errorTimeout = setTimeout(() => {
        closeErrorDisplay();
    }, 5000);
}

function closeErrorDisplay() {
    if (errorDisplay) {
        errorDisplay.classList.remove('show');
    }
}

if (errorCloseBtn) {
    errorCloseBtn.addEventListener('click', closeErrorDisplay);
}

function goBackSafely() {
    const previousPage = document.referrer;

    if (
        previousPage &&
        previousPage.includes(window.location.hostname) &&
        !previousPage.includes('login.html')
    ) {
        window.location.href = previousPage;
    } else if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = 'unauthorized.html';
    }
}

async function adminOnly() {
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

            if (userData.role !== 'administrator' && userData.role !== 'teacher') {
                goBackSafely();
                return;
            } else if (userData.groups && userData.groups.length === 0) {
                window.location.href = 'no_group.html';
                return;
            }

            AppState.userProfile = userData;

        } else if (res.status === 401) {
            logout();
            return;
        } else {
            console.error('Error fetching status.');
            goBackSafely();
            return;
        }
    } catch (error) {
        if (error.name === 'AbortError' || error.message.includes('aborted')) {
            return;
        }

        goBackSafely();
        console.error('Network error:', error);
    }
}

async function requireAuth() {
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

        if (!res.ok) {
            logout();
            return;
        }

        const userData = await res.json();
        AppState.userProfile = userData;

        if (userData.groups && userData.groups.length === 0 && !window.location.href.includes('no_group.html')) {
            window.location.href = 'no_group.html';
            return;
        }

        if (!AppState.currentGroupId && userData.groups && userData.groups.length > 0) {
            AppState.currentGroupId = userData.groups[0].id;
            localStorage.setItem('groupID', AppState.currentGroupId);
        }

    } catch (error) {
        console.error('Network error:', error);
    }
}

async function checkLoginStatus() {
    const token = localStorage.getItem('token');

    if (!token) {
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

            if (userData.groups && userData.groups.length > 0) {
                window.location.href = 'chat.html';
            } else {
                window.location.href = 'no_group.html';
            }
        } else if (res.status === 401) {
            localStorage.removeItem('token');
        }
    } catch (error) {
        console.error(error);
    }
}

function formatMessageTime(rawDateString) {
    if (!rawDateString) return '';

    let safeString = rawDateString.replace(' ', 'T');
    if (!safeString.endsWith('Z') && !safeString.includes('+')) {
        safeString += 'Z';
    }

    const date = new Date(safeString);

    if (isNaN(date.getTime())) return '';

    const timeStr = date.toLocaleTimeString('en-GB', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });

    const dateStr = date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });

    return `${timeStr} - ${dateStr}`;
}
