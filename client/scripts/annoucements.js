const annoucementTemplate = document.getElementById('announcementTemplate');
const displayBox = document.getElementById('displayBox');
const createBtn = document.getElementById('sendBtn');
const createForm = document.getElementById('form');
const cancelBtn = document.getElementById('cancelBtn');
const formTitle = document.getElementById('title-input');
const formContent = document.getElementById('message-input');
const formUrgent = document.getElementById('urgency-input');
const postBtn = document.getElementById('postBtn');

async function LoadAnnoucements() {
    if (AppState.userProfile.role == 'student') createBtn.remove();
    displayBox.innerHTML = '';

    if (!AppState.currentGroupId) return;
    displayBox.innerHTML = '';

    const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/announcement`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
    });

    if (!res.ok) {
        const error = await res.json();
        displayError(`${error.detail}`);
        return;
    } else {
        let data = await res.json();

        data.forEach((element) => {
            let first_name = element.author.first_name;
            let last_name = element.author.last_name;
            let role = element.author.role;
            let title = element.title;
            let content = element.content;
            let urgent = element.urgent;
            let date = element.sent_at;

            addAnnoucement(first_name, last_name, role, title, content, date, urgent);
        });
    }
}

function addAnnoucement(first_name, last_name, role, title, content, date, urgent) {
    const annoucementsNode = annoucementTemplate.content.cloneNode(true).firstElementChild;

    let f = '';
    if (first_name.length > 0) f = first_name[0].toUpperCase();
    let l = '';
    if (last_name.length > 0) l = last_name[0].toUpperCase();

    const options = {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true,
    };

    annoucementsNode.querySelector('.announcement-avatar').textContent = `${f}${l}`;
    annoucementsNode.querySelector('.announcement-user').textContent = `${first_name} ${last_name}`;
    annoucementsNode.querySelector('.announcement-date').textContent = formatMessageTime(date);
    annoucementsNode.querySelector('.annoucement-title').textContent = title;
    annoucementsNode.querySelector('.announcement-content').innerHTML = content;
    annoucementsNode.querySelector('.announcement-role').textContent = role.toUpperCase();

    if (urgent) annoucementsNode.classList.add('urgent');

    displayBox.appendChild(annoucementsNode);
    displayBox.scrollTop = displayBox.scrollHeight;
}

async function createAnnoucement() {
    let title = formTitle.value;
    let content = formContent.value;
    let urgency = formUrgent.checked;

    if (title == '' || content == '') {
        displayError('Title and message fields must be filled');
        return false;
    }

    let res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/announcement`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
            title: title,
            content: content,
            urgent: urgency,
        }),
    });

    if (!res.ok) {
        const error = await res.json();
        displayError(`${error.detail}`);
        return false;
    }

    formTitle.value = '';
    formContent.value = '';
    formUrgent.checked = false;

    return true;
}

createBtn.addEventListener('click', () => {
    createForm.classList.add('form-active');
});

cancelBtn.addEventListener('click', () => {
    createForm.classList.remove('form-active');
});

postBtn.addEventListener('click', async () => {
    const success = await createAnnoucement();

    if (success) {
        createForm.classList.remove('form-active');
        LoadAnnoucements();
    }
});

document.addEventListener('groupChanged', async () => {
    await LoadAnnoucements();
});

async function initAnnouncements() {
    await requireAuth();

    if (AppState.currentGroupId) {
        await LoadAnnoucements();
    }
}

initAnnouncements();
