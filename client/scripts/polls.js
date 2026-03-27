requireAuth();

let currentGroupId=AppState.currentGroupId;
const openModalBtn = document.getElementById('openCreatePollModalBtn');
const createModal = document.getElementById('createPollModal');
const closeModalBtn = document.getElementById('closePollModalBtn');
const cancelPollBtn = document.getElementById('cancelPollBtn');
const postNewPollBtn=document.getElementById("confirmCreatePollBtn");
const formQuestion=document.getElementById("pollQuestion");
const formOptions=document.getElementById("pollOptions");

const pollTemplate = document.getElementById(`pollTemplate`);
const optionTemplate = document.getElementById(`pollOptionTemplate`);
const pollsContainer = document.getElementById('pollsContainer');

openModalBtn.addEventListener('click', () => {
    createModal.classList.add('active');
});

postNewPollBtn.addEventListener("click",async()=>{
    let title=formQuestion.value;
    formQuestion.value="";
    let options=formOptions.value.split(',');
    formOptions.value="";
    if(title=="" || options.length<=1)return;
    let res = await fetch(`${API_BASE_URL}/groups/${currentGroupId}/polls`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
            title: title
        })
    });
    if (!res.ok) {
        console.log("issue when creating new poll");
        return;
    }
    let pollData = await res.json();
    let pollID=pollData.id;
    options.forEach(async(option) =>{
        let res = await fetch(`${API_BASE_URL}/polls/${pollID}/choices`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            },
            body: JSON.stringify({
                text: option,
                manifesto: "",
                photo_url: ""
            })
        });
        if (!res.ok) {
            console.log("issue when adding a new option");
            return;
        }
    })

    await getPolls();
    closeModal();
})

const closeModal = () => {
    createModal.classList.remove('active');
    document.getElementById('pollQuestion').value = '';
    document.getElementById('pollOptions').value = '';
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

    pollContainer.querySelectorAll('.poll-option-card').forEach(c => {
        c.classList.remove('selected');
        c.querySelector('.radio-indicator').innerText = 'radio_button_unchecked';
    });

    card.classList.add('selected');
    card.querySelector('.radio-indicator').innerText = 'radio_button_checked';

    pollContainer.querySelector('.confirm-btn').disabled = false;
}

function submitVote(btn) {
    const pollContainer = btn.closest('.poll-container');
    const pollsList = document.getElementById('pollsContainer');
    const successView = document.getElementById('successView');

    pollsList.style.display = 'none';
    successView.style.display = 'flex';
}

function addPoll(title, options, pollID) {

    const pollNode = pollTemplate.content.cloneNode(true).firstElementChild;
    pollNode.querySelector('.poll-title').textContent = title;
    pollNode.dataset.id = pollID;

    const optionsList = pollNode.querySelector('.options-list');

    options.forEach(optionText => {
        const optionNode = optionTemplate.content.cloneNode(true).firstElementChild;
        optionNode.querySelector('.option-title').textContent = optionText.text;
        //jsp si faut stocker l'id quelque part

        optionNode.addEventListener('click', function () {
            selectOption(this);
        });

        optionsList.appendChild(optionNode);
    });

    pollNode.querySelector('.confirm-btn').addEventListener('click', function () {
        submitVote(this);
    });

    pollsContainer.appendChild(pollNode);
}

async function sendVote(pollID, choiceID) {
    console.log(" starting vote submitted");
    let res = await fetch(`${API_BASE_URL}/polls/${pollID}/vote?choice_id=${choiceID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });
    if (!res.ok) {
        console.log("issue when submitting vote");
        return;
    }
    console.log("vote submitted");
}

async function getPolls() {
    pollsContainer.innerHTML="";
    const res = await fetch(`${API_BASE_URL}/groups/${currentGroupId}/polls`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });
    if(!res.ok){
        console.log("issue with getting polls");
        return;
    }
    let data = await res.json();
    data.forEach(poll =>{
        if(poll.is_active)addPoll(poll.title,poll.choices,poll.id);
    })
}

if (AppState.currentGroupId) {
    setTimeout(async() => {
        await getPolls();
    }, 100);
}