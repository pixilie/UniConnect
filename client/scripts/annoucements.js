requireAuth();
const annoucementTemplate = document.getElementById("announcementTemplate");
const displayBox = document.getElementById("displayBox");
const createBtn = document.getElementById("sendBtn");
const createForm = document.getElementById("form")
const cancelBtn = document.getElementById("cancelBtn");
const formTitle = document.getElementById("title-input");
const formContent = document.getElementById("message-input");
const formUrgent = document.getElementById("urgency-input");
const sendBtn = document.getElementById("postBtn");


async function LoadAnnoucements() {
    const currentGroupId = AppState.currentGroupId;

    if (!currentGroupId) return;

    displayBox.innerHTML = "";
    const res = await fetch(`${API_BASE_URL}/groups/${currentGroupId}/announcement`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });

    if (!res.ok) {
        console.error(`Error while fetching past Annoucements: ${res.status}`);
    } else {
        let data = await res.json();

        data.forEach(element => {
            let first_name = element.author.first_name;
            let last_name = element.author.last_name;
            let role = element.author.role;
            let title = element.title;
            let content = element.content;
            let urgent = element.urgent;
            let date = element.sent_at
            addAnnoucement(first_name, last_name, role, title, content, date, urgent);
        });
    }
}

function addAnnoucement(first_name, last_name, role, title, content, date, urgent) {
    const annoucementsNode = annoucementTemplate.content.cloneNode(true).firstElementChild;

    let f = "";
    if (first_name.length > 0) f = first_name[0].toUpperCase();
    let l = "";
    if (last_name.length > 0) l = last_name[0].toUpperCase();

    const tempDate = new Date(date);

    const options = {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
    };

    const formattedDate = new Intl.DateTimeFormat('en-US', options).format(tempDate);

    annoucementsNode.querySelector(".announcement-avatar").textContent = `${f}${l}`;
    annoucementsNode.querySelector(".announcement-user").textContent = `${first_name} ${last_name}`;
    annoucementsNode.querySelector(".announcement-date").textContent = formattedDate;
    annoucementsNode.querySelector(".annoucement-title").textContent = title;
    annoucementsNode.querySelector(".announcement-content").innerHTML = content;
    annoucementsNode.querySelector(".announcement-role").textContent = role.toUpperCase();

    if (urgent) annoucementsNode.classList.add("urgent");

    displayBox.appendChild(annoucementsNode);
    displayBox.scrollTop = displayBox.scrollHeight;
}

async function createAnnoucement() {
    const currentGroupId = AppState.currentGroupId;

    let title = formTitle.value;
    formTitle.value = "";
    let content = formContent.value;
    formContent.value = "";
    let urgency = formUrgent.checked;
    formUrgent.checked = false;

    await fetch(`${API_BASE_URL}/groups/${currentGroupId}/announcement`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
            title: title,
            content: content,
            urgent: urgency
        })
    });
}

createBtn.addEventListener("click", () => {
    createForm.classList.add("form-active");
});

cancelBtn.addEventListener("click", () => {
    createForm.classList.remove("form-active");
});

sendBtn.addEventListener("click", async () => {
    await createAnnoucement();
    createForm.classList.remove("form-active");
    displayBox.innerHTML = "";
    LoadAnnoucements();
});

if (AppState.currentGroupId) {
    setTimeout(() => {
        LoadAnnoucements();
    }, 100);
}
