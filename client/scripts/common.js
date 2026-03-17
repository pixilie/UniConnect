const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

const API_BASE_URL = isLocal ? "http://localhost:8000/api" : "https://uniconnect.pixilie.net/api";
const WS_BASE_URL = isLocal ? "ws://localhost:8000/ws" : "wss://uniconnect.pixilie.net/ws";

const profileName = document.getElementById("currentUserName");
const profileAvatar = document.getElementById("currentUserAvatar");
const profileRole = document.getElementById("currentUserRole");

const groupList=document.getElementById("groupList");

let profileData;
let username = "";
let groupID=null;

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

async function getCurrentGroup() {
    if(!localStorage.getItem("groupID"))localStorage.setItem("groupID",profileData.groups[0].id);
    groupID= localStorage.getItem("groupID");
}

async function getProfileData() {
    const res = await fetch(`${API_BASE_URL}/users/me`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });

    if (!res.ok) {
        console.log("Issue with getting profile data");
        return;
    }

    profileData = await res.json();

    username = `${profileData.first_name} ${profileData.last_name}`;
    profileName.textContent = username;
    profileAvatar.textContent = `${profileData.first_name.charAt(0).toUpperCase()}${profileData.last_name.charAt(0).toUpperCase()}`;
    profileRole.textContent = profileData.role;
}

async function setGroupList() {
    if(profileData.role="Student")groupList.disable=true;
    for (const group of profileData.groups){

        let name=group.name;
        let id=group.id;

        const option=new Option(name,id);
        groupList.add(option);
    };
    if(localStorage.getItem("groupID")!=null)groupList.value=localStorage.getItem("groupID");
}

groupList.addEventListener("change",function(event){
    console.log(`new group id: ${event.target.value}`)
    localStorage.setItem("groupID",event.target.value);
    groupID=localStorage.getItem("groupID");
    loadPage();
});

window.dataReady = (async () => {
    await getProfileData();
    await getCurrentGroup();
    await setGroupList();
})();
/*
(async () => {
    await getProfileData();
    await getCurrentGroup();
    await setGroupList();
})();*/