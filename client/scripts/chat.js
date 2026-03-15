const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE_URL = isLocal ? "http://localhost:8000/api" : "https://uniconnect.pixilie.net/api";
const WS_BASE_URL = isLocal ? "ws://localhost:8000/ws" : "wss://uniconnect.pixilie.net/ws";

const chat = document.getElementById("chatBox");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const messageTemplate = document.getElementById("messageTemplate");
const profileName = document.getElementById("currentUserName");
const profileAvatar = document.getElementById("currentUserAvatar");
const profileRole = document.getElementById("currentUserRole");

let profileData;
let group_id = 0;
let username = "";
let socket;

function formatMessageTime(rawDateString) {
    if (!rawDateString) return "";

    let safeString = rawDateString.replace(" ", "T");
    if (!safeString.endsWith("Z") && !safeString.includes("+")) {
        safeString += "Z";
    }

    const date = new Date(safeString);

    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

async function WSConnect() {
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

    if (profileData.groups && profileData.groups.length > 0) {
        console.log(profileData.groups[0].id)
        group_id = profileData.groups[0].id;
    } else {
        console.error("User has no groups!");
        window.location.href = "no_group.html";
        return;
    }

    username = `${profileData.first_name} ${profileData.last_name}`;
    profileName.textContent = username;
    profileAvatar.textContent = `${profileData.first_name.charAt(0)}${profileData.last_name.charAt(0)}`;
    profileRole.textContent = profileData.role;

    const token = localStorage.getItem("token");
    socket = new WebSocket(`${WS_BASE_URL}/groups/${group_id}?token=${token}`);

    await new Promise((resolve, reject) => {
        socket.onopen = () => {
            console.log("WebSocket connected");
            resolve();
        };

        socket.onerror = (err) => {
            console.error("WebSocket error:", err);
            reject(err);
        };
    });

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        let first_name = data.author_name.split(' ')[0];
        let last_name = data.author_name.split(' ')[1];

        addMessage(first_name, last_name, data.sent_at, data.content);
    };

    socket.onclose = () => {
        console.log("WebSocket closed");
    };
}

async function sendMessage(message) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        await WSConnect();
    }

    const text = message.trim();

    if (text === "") return;

    if (socket.readyState === WebSocket.OPEN) {
        socket.send(text);
    } else {
        console.log("socket not ready");
    }
}

function addMessage(first_name, last_name, sent_at, text) {
    const messageNode = messageTemplate.content.cloneNode(true);

    messageNode.querySelector(".msg-avatar").textContent = `${first_name[0]}${last_name[0]}`;
    messageNode.querySelector(".msg-user").textContent = `${first_name} ${last_name} - ${formatMessageTime(sent_at)}`;
    messageNode.querySelector(".bubble").textContent = text;

    if (first_name === profileData.first_name && last_name === profileData.last_name) {
        messageNode.querySelector(".message-row").classList.add("me");
    }

    chat.appendChild(messageNode);

    chat.scrollTop = chat.scrollHeight;
}

async function LoadMessages() {
    const res = await fetch(`${API_BASE_URL}/groups/${group_id}/messages?skip=0&limit=-1`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });

    if (!res.ok) {
        console.log(`Error while fetching past messages: ${res}`);
    } else {
        let data = await res.json();
        data.forEach(element => {
            let first_name = element.author.first_name;
            let last_name = element.author.last_name;
            addMessage(first_name, last_name, element.sent_at, element.content);
        });
    }
}

sendBtn.addEventListener("click", () => {
    sendMessage(input.value);
    input.value = "";
});

input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage(input.value);
        input.value = "";
    }
});

(async () => {
    await WSConnect();
    await LoadMessages();
})();
