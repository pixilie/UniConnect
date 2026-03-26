requireAuth();

const openModalBtn = document.getElementById('openCreatePollModalBtn');
const createModal = document.getElementById('createPollModal');
const closeModalBtn = document.getElementById('closePollModalBtn');
const cancelPollBtn = document.getElementById('cancelPollBtn');

const pollTemplate=document.getElementById(`pollTemplate`);
const optionTemplate=document.getElementById(`pollOptionTemplate`);
    const pollsContainer = document.getElementById('pollsContainer');

openModalBtn.addEventListener('click', () => {
    createModal.classList.add('active');
});

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

function addPoll(){
    const pollNode=pollTemplate.cloneNode(true);
}

function submitVote(btn) {
    const pollContainer = btn.closest('.poll-container');
    const pollsList = document.getElementById('pollsContainer');
    const successView = document.getElementById('successView');

    pollsList.style.display = 'none';
    successView.style.display = 'flex';
}

function addPoll(title,options,pollID) {

    const pollNode = pollTemplate.content.cloneNode(true).firstElementChild;
    pollNode.querySelector('.poll-title').textContent = title;
    pollNode.dataset.id=pollID;

    const optionsList = pollNode.querySelector('.options-list');

    options.forEach(optionText => {
        const optionNode = optionTemplate.content.cloneNode(true).firstElementChild;
        optionNode.querySelector('.option-title').textContent = optionText;
        
        optionNode.addEventListener('click', function() {
            selectOption(this);
        });

        optionsList.appendChild(optionNode);
    });

    pollNode.querySelector('.confirm-btn').addEventListener('click', function() {
        submitVote(this);
    });

    pollsContainer.appendChild(pollNode);
}

async function sendVote(pollID,choiceID) {
    let res= await fetch(`/api/polls/${pollID}/vote?choice_id=${choiceID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if(!res.ok){
        console.log("issue when submitting vote");
        return;
    }
    
    
}
