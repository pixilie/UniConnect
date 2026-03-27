requireAuth();

let currentDisplayedMonday = getMonday(new Date());
let allEvents = [];

const calendarGrid = document.getElementById('calendarGrid');
const eventTemplate = document.getElementById('eventTemplate');
const currentWeekLabel = document.getElementById('currentWeekLabel');
const prevWeekBtn = document.getElementById('prevWeekBtn');
const nextWeekBtn = document.getElementById('nextWeekBtn');

const openModalBtn = document.getElementById('openCreateEventModalBtn');
const createModal = document.getElementById('createEventModal');
const closeModalBtn = document.getElementById('closeEventModalBtn');
const cancelEventBtn = document.getElementById('cancelEventBtn');
const confirmCreateBtn = document.getElementById('confirmCreateEventBtn');

function getMonday(d) {
    const date = new Date(d);
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(date.getFullYear(), date.getMonth(), diff, 0, 0, 0, 0);
}

function formatShortDate(date) {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function updateCalendarHeaders() {
    let friday = new Date(currentDisplayedMonday);
    friday.setDate(currentDisplayedMonday.getDate() + 4);

    currentWeekLabel.textContent = `${formatShortDate(currentDisplayedMonday)} - ${formatShortDate(friday)}, ${currentDisplayedMonday.getFullYear()}`;

    const days = ['mon', 'tue', 'wed', 'thu', 'fri'];
    days.forEach((dayId, index) => {
        let d = new Date(currentDisplayedMonday);
        d.setDate(currentDisplayedMonday.getDate() + index);
        document.getElementById(`date-${dayId}`).textContent = d.getDate();
    });
}

function clearGrid() {
    const cards = calendarGrid.querySelectorAll('.event-card');
    cards.forEach(card => card.remove());
}

function renderEventCard(evt) {
    const startDate = new Date(evt.start);
    const endDate = new Date(evt.end);

    const eventMonday = getMonday(startDate);
    if (eventMonday.getTime() !== currentDisplayedMonday.getTime()) return;

    const dayIndex = startDate.getDay();
    if (dayIndex === 0 || dayIndex === 6) return;
    const gridColumn = dayIndex + 1;

    const startHour = startDate.getHours();
    if (startHour < 8 || startHour >= 18) return;
    const gridRowStart = startHour - 6;

    let durationHours = Math.round((endDate - startDate) / (1000 * 60 * 60));
    if (durationHours < 1) durationHours = 1;

    let gridRowEnd = gridRowStart + durationHours;
    if (gridRowEnd > 12) gridRowEnd = 12;

    const eventNode = eventTemplate.content.cloneNode(true).firstElementChild;
    eventNode.classList.add(`type-${evt.type}`);

    eventNode.style.gridColumn = gridColumn;
    eventNode.style.gridRow = `${gridRowStart} / ${gridRowEnd}`;

    eventNode.querySelector('.event-time').textContent = `${startHour}:00 - ${startHour + durationHours}:00`;
    eventNode.querySelector('.event-title').textContent = evt.title;
    eventNode.querySelector('.event-location').textContent = evt.location || "TBD";

    calendarGrid.appendChild(eventNode);
}

function refreshWeekView() {
    clearGrid();
    updateCalendarHeaders();
    allEvents.forEach(evt => renderEventCard(evt));
}

prevWeekBtn.addEventListener('click', () => {
    currentDisplayedMonday.setDate(currentDisplayedMonday.getDate() - 7);
    refreshWeekView();
});

nextWeekBtn.addEventListener('click', () => {
    currentDisplayedMonday.setDate(currentDisplayedMonday.getDate() + 7);
    refreshWeekView();
});

const closeModal = () => {
    createModal.classList.remove('active');
    document.getElementById('eventTitle').value = '';
    document.getElementById('eventLocation').value = '';
    document.getElementById('eventStart').value = '';
    document.getElementById('eventEnd').value = '';
};

openModalBtn.addEventListener('click', () => createModal.classList.add('active'));
closeModalBtn.addEventListener('click', closeModal);
cancelEventBtn.addEventListener('click', closeModal);

confirmCreateBtn.addEventListener('click', async () => {
    const title = document.getElementById('eventTitle').value.trim();
    const startInput = document.getElementById('eventStart').value;
    const endInput = document.getElementById('eventEnd').value;
    const type = document.getElementById('eventType').value;
    const location = document.getElementById('eventLocation').value.trim();

    if (!title || !startInput || !endInput) return alert("Fill all required fields");

    const startDate = new Date(startInput);
    const endDate = new Date(endInput);

    if (endDate <= startDate) return alert("End time must be after start time.");

    confirmCreateBtn.disabled = true;

    // TODO: API FASTAPI - POST NEW EVENT

    const newEvent = {
        title: title,
        type: type,
        start: startInput,
        end: endInput,
        location: location
    };

    allEvents.push(newEvent);
    currentDisplayedMonday = getMonday(startDate);
    refreshWeekView();
    closeModal();
    confirmCreateBtn.disabled = false;
});

async function fetchEvents() {
    const currentGroupId = AppState.currentGroupId;
    if (!currentGroupId) return;

    // TODO: API FASTAPI - GET ALL EVENTS => Events + Schedules (.ics) donc 2 appels a faire

    // Remplacer ces données "en dur" par le résultat du fetch API
    allEvents = [
        { title: "Graph Theory", type: "course", start: "2026-03-30T08:00:00", end: "2026-03-30T10:00:00", location: "Amphi B" },
        { title: "Linear Algebra", type: "course", start: "2026-03-31T10:00:00", end: "2026-03-31T12:00:00", location: "Room 204" },
        { title: "Algebra Revision", type: "study", start: "2026-03-31T14:00:00", end: "2026-03-31T16:00:00", location: "Cafeteria" }
    ];

    refreshWeekView();
}

document.addEventListener("groupChanged", () => {
    fetchEvents();
});

if (AppState.currentGroupId) {
    setTimeout(() => {
        fetchEvents();
    }, 100);
}
