const chat=document.getElementById("chat");
const input=document.getElementById("input");
const sendTemplate=document.getElementById("SendTemplate");
const receiveTemplate=document.getElementById("ReceiveTemplate");
let profileData;
let group_id=0;
let username="";
let socket;

async function WSConnect() {
    const res = await fetch("https://uniconnect.pixilie.net/api/users/me", {
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
    group_id = profileData.id;
    username = `${profileData.first_name} ${profileData.last_name}`;

    socket = new WebSocket(`wss://uniconnect.pixilie.net/ws/groups/${group_id}`);

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
        let user = data.author_name;

        if (user == username) addMessageMe(user, data.content);
        else addMessageOther(user, data.content);
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
    }
    else console.log("socket not ready");
}

function addMessageMe(username, text) {

  const messageNode = sendTemplate.content.cloneNode(true);

  messageNode.querySelector(".username").textContent = username;
  messageNode.querySelector(".text").textContent = text;

  chat.appendChild(messageNode);
}

function addMessageOther(username, text) {

  const messageNode = receiveTemplate.content.cloneNode(true);

  messageNode.querySelector(".username").textContent = username;
  messageNode.querySelector(".text").textContent = text;

  chat.appendChild(messageNode);
}

async function LoadMessages() {
    const res = await fetch(`https://uniconnect.pixilie.net/api/groups/${group_id}/messages`, {
        method: "GET",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });
    if(!res.ok)console.log("Issue with getting all messages");
    else{
        let data= await res.json();
        data.forEach(element => {
            let user = element.username;
            if(user=username)addMessageMe(user,element.content);
            else addMessageOther(user,element.content);
        });
    }

}

(async () => {
    await WSConnect();
    await LoadMessages();
})();