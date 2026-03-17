requireAuth();

const chat = document.getElementById("chatBox");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const messageTemplate = document.getElementById("messageTemplate");

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

    const token = localStorage.getItem("token");
    console.log(`WS group id: ${groupID}`);
    socket = new WebSocket(`${WS_BASE_URL}/groups/${groupID}?token=${token}`);

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

    let f="";
    if(first_name.length>0)f=first_name[0].toUpperCase();
    let l="";
    if(last_name.length>0)l=last_name[0].toUpperCase();
    messageNode.querySelector(".msg-avatar").textContent = `${f}${l}`;
    messageNode.querySelector(".msg-user").textContent = `${first_name} ${last_name} - ${formatMessageTime(sent_at)}`;
    messageNode.querySelector(".bubble").textContent = text;

    if (first_name === profileData.first_name && last_name === profileData.last_name) {
        messageNode.querySelector(".message-row").classList.add("me");
    }

    chat.appendChild(messageNode);

    chat.scrollTop = chat.scrollHeight;
}

async function LoadMessages() {
    chat.innerHTML="";
    const res = await fetch(`${API_BASE_URL}/groups/${groupID}/messages`, {
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

async function loadPage() {
    if(socket)socket.close();
    await WSConnect();
    await LoadMessages();
}

(async () => {
  await window.dataReady;
  console.log("common finished");
  // safe to use data here
  loadPage();
})();
//loadPage();