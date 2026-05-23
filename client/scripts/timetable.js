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

let currentDisplayedMonday = getMonday(new Date());
let allEvents = [];
let weekEvents = Array.from({ length: 7 }, () =>
    Array.from({ length: 24 }, () =>
        Array.from({ length: 0 }, () => null)
    )
);

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
    let sunday = new Date(currentDisplayedMonday);
    sunday.setDate(currentDisplayedMonday.getDate() + 6);

    currentWeekLabel.textContent = `${formatShortDate(currentDisplayedMonday)} - ${formatShortDate(sunday)}, ${currentDisplayedMonday.getFullYear()}`;

    const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
    days.forEach((dayId, index) => {
        let d = new Date(currentDisplayedMonday);
        d.setDate(currentDisplayedMonday.getDate() + index);
        document.getElementById(`date-${dayId}`).textContent = d.getDate();
    });
}

function clearGrid() {
    const cards = calendarGrid.querySelectorAll('.event-card');
    cards.forEach((card) => card.remove());
    weekEvents = Array.from({ length: 7 }, () =>
        Array.from({ length: 24 }, () =>
            Array.from({ length: 0 }, () => null)
        )
    );
}

function storeEvent(evt) {
    let startDate = new Date(evt.start);
    let endDate = new Date(evt.end);

    const eventMonday = getMonday(startDate);
    if (eventMonday.getTime() !== currentDisplayedMonday.getTime()) {
        return;
    };

    let day = startDate.getDay();
    let startHour = startDate.getHours();
    let endHour = endDate.getHours();
    if (endHour == 0) endHour = 24;

    for (let index = startHour; index < endHour; index++) {
        weekEvents[day][index].push(evt);
        weekEvents[day][index].forEach((item) => {
            if (item['overlap'] > weekEvents[day][index].length) { }
            else {
                item['overlap'] = weekEvents[day][index].length;
                if (!('overlapOrder' in item)) item['overlapOrder'] = weekEvents[day][index].length;
            }
        });
    }
}

async function deleteEvent(id) {
    try {
        const res = await fetch(`${API_BASE_URL}/events/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${localStorage.getItem('token')}`,
            }
        });

        if (!res.ok) {
            const error = await res.json();
            displayError(`${error.detail}`);
            return;
        }
        else {
            fetchEvents();
            refreshWeekView();
        }

    } catch (error) {
        console.error("Failed to delete event :", error.message);
    }
}

function splitEventDays(evt) {
    const startDate = new Date(evt.start);
    const endDate = new Date(evt.end);
    const startDay = startDate.toDateString();
    const endDay = endDate.toDateString();

    // Check if the event is on a single day
    if (startDay === endDay) {
        storeEvent(evt);
    }
    else if (endDate.getHours() === 0 && endDate.getMinutes() === 0 && (endDate - startDate) <= 86400000) {
        storeEvent(evt);
    }
    else {
        const splitDate = new Date(
            startDate.getFullYear(),
            startDate.getMonth(),
            startDate.getDate() + 1,
            0, // Hours
            0, // Minutes
            0  // Seconds
        );

        let startEvent = {
            ...evt,
            end: splitDate,
            displayStart: evt.displayStart || evt.start,
            displayEnd: evt.displayEnd || evt.end
        };

        let endEvent = {
            ...evt,
            start: splitDate,
            displayStart: evt.displayStart || evt.start,
            displayEnd: evt.displayEnd || evt.end
        };

        storeEvent(startEvent);
        splitEventDays(endEvent);
    }
}

function renderEventCard(evt) {
    const startDate = new Date(evt.start);
    const endDate = new Date(evt.end);
    let displayStart = new Date(evt.start);
    let displayEnd = new Date(evt.end);

    if ('displayStart' in evt) {
        displayStart = new Date(evt.displayStart);
    }
    if ('displayEnd' in evt) {
        displayEnd = new Date(evt.displayEnd);
    }

    const eventMonday = getMonday(startDate);
    if (eventMonday.getTime() !== currentDisplayedMonday.getTime()) return;

    const dayIndex = startDate.getDay();
    const gridColumn = dayIndex === 0 ? 8 : dayIndex + 1;

    const startHour = startDate.getHours();

    const gridRowStart = startHour + 2;

    let durationHours = Math.round((endDate - startDate) / (1000 * 60 * 60));
    if (durationHours < 1) durationHours = 1;
    if (endDate.getHours()==0) durationHours+=1;
    let gridRowEnd = gridRowStart + durationHours;
    if (gridRowEnd > 26) gridRowEnd = 26;

    const eventNode = eventTemplate.content.cloneNode(true).firstElementChild;
    eventNode.classList.add(`type-${evt.type.toLowerCase()}`);

    eventNode.style.gridColumn = gridColumn;
    eventNode.style.gridRow = `${gridRowStart} / ${gridRowEnd}`;

    eventNode.querySelector('.event-time').textContent =
        `${displayStart.getHours()}:00 - ${displayEnd.getHours()}:00`;
    eventNode.querySelector('.event-title').textContent = evt.title;
    eventNode.querySelector('.event-location').textContent = evt.location || 'TBD';

    eventNode.addEventListener('click', () => {
        document.getElementById('viewEventTitle').textContent = evt.title;
        document.getElementById('viewEventTime').textContent =
            `${formatShortDate(displayStart)} ${formatShortDate(displayStart) != formatShortDate(displayEnd) ? `- ${formatShortDate(displayEnd)}` : ''}
      • ${displayStart.getHours()}:00 - ${displayEnd.getHours()}:00`;
        document.getElementById('viewEventLocation').textContent = evt.location || 'No location';
        document.getElementById('viewEventType').textContent = evt.type;
        document.getElementById('viewEventDescription').textContent =
            evt.description || 'No description provided.';

        document.getElementById('viewEventModal').classList.add('active');
        if (!Object.hasOwn(evt, 'id') || AppState.userProfile.role=="student"){
            document.getElementById('viewEventDeleteBtn').style.display='none';
        }
        else{
            document.getElementById('viewEventDeleteBtn').style.display='inline';
            document.getElementById('viewEventDeleteBtn').onclick = () => {
                deleteEvent(evt.id);
                viewEventModal.classList.remove('active');
            };
        }
    });

    eventNode.style.marginLeft = `${(evt.overlapOrder - 1) * (100 / evt.overlap)}%`;
    eventNode.style.marginRight = `${(evt.overlap - evt.overlapOrder) * (100 / evt.overlap)}%`;

    calendarGrid.appendChild(eventNode);
}

function refreshWeekView() {
    clearGrid();
    updateCalendarHeaders();
    allEvents.forEach((evt) => splitEventDays(evt));
    for (let i = 0; i < weekEvents.length; i++) {
        for (let j = 0; j < weekEvents[i].length; j++) {
            for (let h = 0; h < weekEvents[i][j].length; h++) {
                let startDate = new Date(weekEvents[i][j][h].start);
                if (startDate.getHours() == j) {
                    renderEventCard(weekEvents[i][j][h])
                }
            }
        }
    }
}

prevWeekBtn.addEventListener('click', () => {
    currentDisplayedMonday.setDate(currentDisplayedMonday.getDate() - 7);
    refreshWeekView();
});

nextWeekBtn.addEventListener('click', () => {
    currentDisplayedMonday.setDate(currentDisplayedMonday.getDate() + 7);
    refreshWeekView();
});

const closeViewModalBtn = document.getElementById('closeViewEventModalBtn');
const viewEventModal = document.getElementById('viewEventModal');

closeViewModalBtn.addEventListener('click', () => {
    viewEventModal.classList.remove('active');
});

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('create-modal-overlay')) {
        viewEventModal.classList.remove('active');
    }
});

const closeModal = () => {
    createModal.classList.remove('active');
    document.getElementById('eventTitle').value = '';
    document.getElementById('eventDescription').value = '';
    document.getElementById('eventLocation').value = '';
    document.getElementById('eventStart').value = '';
    document.getElementById('eventEnd').value = '';
};

openModalBtn.addEventListener('click', () => createModal.classList.add('active'));
closeModalBtn.addEventListener('click', closeModal);
cancelEventBtn.addEventListener('click', closeModal);

confirmCreateBtn.addEventListener('click', async () => {
    const title = document.getElementById('eventTitle').value.trim();
    const description = document.getElementById('eventDescription').value.trim();
    const startInput = document.getElementById('eventStart').value;
    const endInput = document.getElementById('eventEnd').value;
    const type = document.getElementById('eventType').value;
    const location = document.getElementById('eventLocation').value.trim();

    if (!title || !startInput || !endInput) return displayError('Fill all required fields');

    const startDate = new Date(startInput);
    const endDate = new Date(endInput);

    if (endDate <= startDate) return displayError('End time must be after start time.');

    confirmCreateBtn.disabled = true;

    const newEvent = {
        title: title,
        description: description,
        start: startInput,
        end: endInput,
        type: type,
        location: location,
    };

    let res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/events`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(newEvent),
    });

    if (!res.ok) {
        const error = await res.json();
        displayError(`${error.detail}`);
        return;
    }
    weekEvents = Array.from({ length: 7 }, () =>
        Array.from({ length: 24 }, () =>
            Array.from({ length: 0 }, () => null)
        )
    );

    const result=await res.json();
    const AddedEvent = {
        title: title,
        description: description,
        start: startInput,
        end: endInput,
        type: type,
        location: location,
        id:result.id
    };

    allEvents.push(AddedEvent);
    currentDisplayedMonday = getMonday(startDate);
    refreshWeekView();
    closeModal();
    confirmCreateBtn.disabled = false;
});

async function fetchEvents() {
    if (!AppState.currentGroupId) return;

    allEvents = [];
    weekEvents = Array.from({ length: 7 }, () =>
        Array.from({ length: 24 }, () =>
            Array.from({ length: 0 }, () => null)
        )
    );

    try {
        const resIcs = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/schedules`, {
            method: 'GET',
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });

        if (resIcs.ok) {
            const scheduleData = await resIcs.text();
            allEvents = parseICSFromString(scheduleData);
        }
        else if (!resIcs.status == 404) {
            const error = await resIcs.json();
            displayError(`${error.detail}`);
            return;
        }

    } catch (error) {
        console.error('Failed to fetch schedule:', error);
    }

    try {
        const resDb = await fetch(
            `${API_BASE_URL}/events?group_id=${AppState.currentGroupId}&skip=0&limit=100`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${localStorage.getItem('token')}`,
                },
            },
        );

        if (resDb.ok) {
            const eventsData = await resDb.json();
            eventsData.forEach((element) => {
                let newElement = {
                    title: element.title,
                    description: element.description,
                    type: element.type,
                    start: element.start,
                    end: element.end,
                    location: element.location,
                    id: element.id
                };
                allEvents.push(newElement);
            });
        }
        else {
            const error = await resDb.json();
            displayError(`${error.detail}`);
            return;
        }
    } catch (error) {
        console.error('Failed to fetch events from DB:', error);
    }

    refreshWeekView();
}

function parseICSFromString(icsString) {
    const jcalData = ICAL.parse(icsString);
    const comp = new ICAL.Component(jcalData);
    const events = comp.getAllSubcomponents('vevent');

    return events.map((event) => {
        const e = new ICAL.Event(event);

        return {
            title: e.summary,
            description: e.description,
            type: 'COURSE',
            start: e.startDate.toJSDate().toISOString(),
            end: e.endDate.toJSDate().toISOString(),
            location: e.location,
        };
    });
}

document.addEventListener('groupChanged', async () => {
    await fetchEvents();
});

async function initTimetables() {
    await requireAuth();

    if (AppState.userProfile && AppState.userProfile.role === 'student') {
        if (openModalBtn) {
            openModalBtn.style.display = 'none';
        }
    }

    if (AppState.userProfile && AppState.userProfile.role === 'student' || AppState.userProfile.role === 'delegate') {
        const typeSelect = document.getElementById('eventType');
        if (typeSelect) {
            typeSelect.value = 'ACTIVITY';
            typeSelect.disabled = true;
        }
    }

    if (AppState.currentGroupId) {
        await fetchEvents();
    }
}

initTimetables();
