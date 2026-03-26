requireAuth();

const openModalBtn = document.getElementById('openCreatePollModalBtn');
const createModal = document.getElementById('createPollModal');
const closeModalBtn = document.getElementById('closePollModalBtn');
const cancelPollBtn = document.getElementById('cancelPollBtn');

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

function submitVote(btn) {
    const pollContainer = btn.closest('.poll-container');
    const pollsList = document.getElementById('pollsContainer');
    const successView = document.getElementById('successView');

    pollsList.style.display = 'none';
    successView.style.display = 'flex';
}
