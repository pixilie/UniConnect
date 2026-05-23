const openModalBtn = document.getElementById('openCreatePollModalBtn');
const createModal = document.getElementById('createPollModal');
const closeModalBtn = document.getElementById('closePollModalBtn');
const cancelPollBtn = document.getElementById('cancelPollBtn');
const postNewPollBtn = document.getElementById('confirmCreatePollBtn');
const formQuestion = document.getElementById('pollQuestion');
const formOptions = document.getElementById('pollOptions');
const pollTemplate = document.getElementById(`pollTemplate`);
const optionTemplate = document.getElementById(`pollOptionTemplate`);
const pollsContainer = document.getElementById('pollsContainer');

let currentGroupId = AppState.currentGroupId;

openModalBtn.addEventListener('click', () => {
    createModal.classList.add('active');
});

postNewPollBtn.addEventListener('click', async () => {
    const endInput = document.getElementById("formEndDate");

    let title = formQuestion.value;
    if (!title || !formOptions.value || !endInput.value) return displayError('Please fill in the title, options and end date.');

    const now = new Date();
    const endDate = new Date(endInput.value);
    const endString = endDate.toISOString();

    if (endDate <= now) {
        displayError("The deadline cannot be in the past");
        endInput.value = '';
        return;
    }

    const options = formOptions.value
        .split(',')
        .map((opt) => opt.trim())
        .filter((opt) => opt.length > 0);

    if (options.length < 2) {
        displayError("A poll must have at least two valid options separated by commas.");
        return;
    }

    formOptions.value = '';
    endInput.value = '';

    let res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/polls`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
            title: title,
            end_datetime: endString
        }),
    });

    if (!res.ok) {
        const error = await res.json();
        displayError(`${error.detail}`);
        return;
    }

    let pollData = await res.json();
    let pollID = pollData.id;

    options.forEach(async (option) => {
        let res = await fetch(`${API_BASE_URL}/polls/${pollID}/choices`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify({
                text: option,
                manifesto: '',
                photo_url: '',
            }),
        });

        if (!res.ok) {
            const error = await res.json();
            displayError(`${error.detail}`);
            return;
        }
    });

    setTimeout(async () => {
        await getPolls();
    }, 100);

    closeModal();
});

const closeModal = () => {
    createModal.classList.remove('active');
    document.getElementById('pollQuestion').value = '';
    document.getElementById('pollOptions').value = '';
    document.getElementById("formEndDate").value = '';
};

closeModalBtn.addEventListener('click', closeModal);
cancelPollBtn.addEventListener('click', closeModal);

createModal.addEventListener('click', (e) => {
    if (e.target === createModal) {
        closeModal();
    }
});

function selectOption(card) {
    const pollContainer = card.closest('.poll-container');

    pollContainer.querySelectorAll('.poll-option-card').forEach((c) => {
        c.classList.remove('selected');
        c.querySelector('.radio-indicator').innerText = 'radio_button_unchecked';
    });

    card.classList.add('selected');
    card.querySelector('.radio-indicator').innerText = 'radio_button_checked';

    pollContainer.querySelector('.confirm-btn').disabled = false;
}

async function submitVote(btn) {
    const pollContainer = btn.closest('.poll-container');
    const pollsList = document.getElementById('pollsContainer');
    const successView = document.getElementById('successView');
    const selected = pollContainer.querySelector('.selected');

    await sendVote(pollContainer.dataset.id, selected.dataset.id);

    pollsList.style.display = 'none';
    successView.style.display = 'flex';
}

function addPoll(title, options, pollID, voted, votedID) {
    const pollNode = pollTemplate.content.cloneNode(true).firstElementChild;

    pollNode.querySelector('.poll-title').textContent = title;
    pollNode.dataset.id = pollID;

    if (voted) {
        pollNode.querySelector(`.timer-badge`).textContent = 'Voted';
        pollNode.querySelector(`.timer-badge`).style.color = 'green';
        pollNode.querySelector(`.timer-badge`).style.backgroundColor = '#79ff58';
    }

    const optionsList = pollNode.querySelector('.options-list');
    let selectedOptionObject = null;

    options.forEach((option) => {
        const optionNode = optionTemplate.content.cloneNode(true).firstElementChild;
        optionNode.querySelector('.option-title').textContent = option.text;
        optionNode.dataset.id = option.id;

        if (!voted) {
            optionNode.addEventListener('click', function () {
                selectOption(this);
            });
        } else {
            if (option.id == votedID) {
                selectedOptionObject = optionNode;
            }
        }
        optionsList.appendChild(optionNode);
    });

    if (selectedOptionObject) selectOption(selectedOptionObject);

    pollNode.querySelector('.confirm-btn').addEventListener('click', function () {
        submitVote(this);
    });

    if (voted) {
        pollNode.querySelector('.confirm-btn').remove();
    }

    pollsContainer.appendChild(pollNode);
}

async function sendVote(pollID, choiceID) {
    let res = await fetch(`${API_BASE_URL}/polls/${pollID}/vote?choice_id=${choiceID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
    });
    if (!res.ok) {
        const error = await res.json();
        displayError(`${error.detail}`);
        return;
    }
}

async function getPolls() {
    if (AppState.userProfile.role == 'student') openModalBtn.remove();

    pollsContainer.innerHTML = '';

    const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/polls`, {
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
    }

    let data = await res.json();

    data.forEach((poll) => {
        if (poll.is_active)
            addPoll(poll.title, poll.choices, poll.id, poll.has_voted, poll.choice_selected);
    });
}

document.addEventListener('groupChanged', async (e) => {
    console.log('test');
    await getPolls();
});

async function initPolls() {
    await requireAuth();

    if (AppState.currentGroupId) {
        await getPolls();
    }
}

initPolls();
