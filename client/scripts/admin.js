requireAuth();
adminOnly();

const adminUserName = document.getElementById('adminUserName');
const adminUserAvatar = document.getElementById('adminUserAvatar');
const adminUserRole = document.getElementById('adminUserRole');
const searchInput = document.getElementById('adminSearchInput');
const groupListContainer = document.getElementById('adminGroupList');
const groupItemTemplate = document.getElementById('adminGroupItemTemplate');
const topBarTitle = document.getElementById('adminTopBarTitle');

const studentListContainer = document.getElementById('studentListContainer');
const studentItemTemplate = document.getElementById('studentItemTemplate');

searchInput.addEventListener('input', (e) => {
  const filter = e.target.value.toLowerCase();
  const items = groupListContainer.querySelectorAll('.group-item');

  items.forEach((item) => {
    const groupName = item.querySelector('.group-name').textContent.toLowerCase();
    if (groupName.includes(filter)) {
      item.style.display = 'flex';
    } else {
      item.style.display = 'none';
    }
  });
});

async function loadAdminData() {
  const token = localStorage.getItem('token');
  if (!token) return;

  try {
    const res = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      const error = await res.json();
      window.alert(`Error while loading admin data: ${error}`);
      return;
    }

    const profileData = await res.json();

    adminUserName.textContent = `${profileData.first_name} ${profileData.last_name}`;
    adminUserAvatar.textContent =
      `${profileData.first_name.charAt(0)}${profileData.last_name.charAt(0)}`.toUpperCase();
    adminUserRole.textContent = profileData.role === 'teacher' ? 'administrator' : profileData.role;

    populateAdminGroups(profileData.groups);
  } catch (error) {
    console.error('Error loading admin data:', error);
  }
}

function populateAdminGroups(groups) {
  if (!groups || groups.length === 0) return;
  groupListContainer.innerHTML = '';

  let currentGroupId = localStorage.getItem('groupID') || groups[0].id.toString();

  groups.forEach((group) => {
    const groupNode = groupItemTemplate.content.cloneNode(true).firstElementChild;

    groupNode.querySelector('.group-name').textContent = group.name;
    groupNode.dataset.groupId = group.id;

    if (group.id.toString() === currentGroupId) {
      groupNode.classList.add('active');
      topBarTitle.textContent = `Admin Panel: ${group.name}`;
      AppState.currentGroupId = group.id.toString();
    }

    groupNode.addEventListener('click', (e) => {
      e.preventDefault();

      const allItems = groupListContainer.querySelectorAll('.group-item');
      allItems.forEach((i) => i.classList.remove('active'));

      groupNode.classList.add('active');
      topBarTitle.textContent = `Admin Panel: ${group.name}`;

      localStorage.setItem('groupID', group.id.toString());
      AppState.currentGroupId = group.id.toString();

      const groupChangeEvent = new CustomEvent('groupChanged', {
        detail: { newId: group.id.toString() },
      });

      document.dispatchEvent(groupChangeEvent);
    });

    groupListContainer.appendChild(groupNode);
  });
}

async function loadStudents() {
  if (!AppState.currentGroupId) return;

  const members = [];

  studentListContainer.innerHTML = '';
  const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/members`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while fetching group members: ${error}`);
  } else {
    let data = await res.json();

    data.forEach((member) => {
      let newMember = {
        id: member.id,
        first_name: member.first_name,
        last_name: member.last_name,
        email: member.email,
        role: member.role,
      };
      members.push(newMember);
    });
  }

  members.forEach((member) => renderStudent(member));
}

function renderStudent(member) {
  const studentNode = studentItemTemplate.content.cloneNode(true).firstElementChild;

  const initials = `${member.first_name.charAt(0)}${member.last_name.charAt(0)}`.toUpperCase();
  const avatar = studentNode.querySelector('.mini-avatar');
  avatar.textContent = initials;
  avatar.style.background = '#6750A4';

  const nameSpan = studentNode.querySelector('.student-name');
  nameSpan.textContent = `${member.first_name} ${member.last_name}`;

  const actionsContainer = studentNode.querySelector('.student-actions');

  if (member.role === 'delegate') {
    const badge = document.createElement('small');
    badge.textContent = 'DELEGATE';
    badge.style.cssText =
      'background:#EADDFF; padding: 2px 6px; border-radius:4px; margin-left:8px; color:#21005D;';
    nameSpan.after(badge);

    const btnRemove = document.createElement('button');

    btnRemove.className = 'btn-ghost-error';
    btnRemove.textContent = 'Remove Delegate';
    btnRemove.onclick = () => promoteToDelegate(member.id, false);
    actionsContainer.appendChild(btnRemove);
  } else {
    const btnPromote = document.createElement('button');

    btnPromote.className = 'btn-action btn-outline';
    btnPromote.style.fontSize = '11px';
    btnPromote.textContent = 'Set Delegate';
    btnPromote.onclick = () => promoteToDelegate(member.id, true);
    actionsContainer.appendChild(btnPromote);
  }

  const btnKick = document.createElement('button');

  btnKick.className = 'btn-ghost-error';
  btnKick.style.fontWeight = 'bold';
  btnKick.style.marginLeft = '12px';
  btnKick.textContent = 'Kick';
  btnKick.onclick = () => kickStudent(member.id);
  actionsContainer.appendChild(btnKick);
  studentListContainer.appendChild(studentNode);
}

const btnCreateGroup = document.getElementById('btnCreateGroup');
const btnAddStudent = document.getElementById('btnAddStudentBtn');
const btnUpdateTimetable = document.getElementById('btnUpdateTimetable');
const btnAddEventBtn = document.getElementById('btnAddEventBtn');
const btnStartElection = document.getElementById('btnStartElection');

const createGroupModal = document.getElementById('createGroupModal');
const addStudentModal = document.getElementById('addStudentModal');
const updateTimetableModal = document.getElementById('updateTimetableModal');
const addEventModal = document.getElementById('addEventModal');
const startElectionModal = document.getElementById('startElectionModal');

const closeAllAdminModals = () => {
  createGroupModal.classList.remove('active');
  addStudentModal.classList.remove('active');
  updateTimetableModal.classList.remove('active');
  addEventModal.classList.remove('active');
  startElectionModal.classList.remove('active');

  document.getElementById('newGroupName').value = '';
  document.getElementById('newStudentEmail').value = '';
  document.getElementById('timetableFile').value = '';
  document.getElementById('electionTitle').value = '';
  document.getElementById('electionOptions').value = '';
  document.getElementById('eventTitle').value = '';
  document.getElementById('eventLocation').value = '';
  document.getElementById('eventStart').value = '';
  document.getElementById('eventEnd').value = '';
};

btnCreateGroup.addEventListener('click', () => createGroupModal.classList.add('active'));

btnAddStudent.addEventListener('click', () => {
  if (!AppState.currentGroupId) return alert('Please select a group first.');
  addStudentModal.classList.add('active');
});

btnUpdateTimetable.addEventListener('click', () => {
  if (!AppState.currentGroupId) return alert('Select a group first.');
  updateTimetableModal.classList.add('active');
});

btnAddEventBtn.addEventListener('click', () => {
  if (!AppState.currentGroupId) return alert('Select a group first.');
  addEventModal.classList.add('active');
});

btnStartElection.addEventListener('click', () => {
  if (!AppState.currentGroupId) return alert('Select a group first.');
  startElectionModal.classList.add('active');
});

document.getElementById('closeGroupModalBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('cancelGroupBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('closeStudentModalBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('cancelStudentBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('closeTimetableModalBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('cancelTimetableBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('closeEventModalBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('cancelEventBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('closeElectionModalBtn').addEventListener('click', closeAllAdminModals);
document.getElementById('cancelElectionBtn').addEventListener('click', closeAllAdminModals);

window.addEventListener('click', (e) => {
  if (e.target.classList.contains('create-modal-overlay')) {
    closeAllAdminModals();
  }
});

document.getElementById('confirmCreateGroupBtn').addEventListener('click', async () => {
  const groupName = document.getElementById('newGroupName').value.trim();
  if (!groupName) return alert('Please enter a group name.');
  const btn = document.getElementById('confirmCreateGroupBtn');

  btn.disabled = true;
  btn.textContent = 'Creating...';

  const res = await fetch(`${API_BASE_URL}/groups/?group_name=${groupName}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while creating new group: ${error}`);
  } else {
    closeAllAdminModals();
    btn.disabled = false;
    btn.textContent = 'Create';
  }

  loadAdminData();
});

document.getElementById('confirmAddStudentBtn').addEventListener('click', async () => {
  const studentEmail = document.getElementById('newStudentEmail').value.trim();
  if (!studentEmail) return alert("Please enter the student's email.");
  const btn = document.getElementById('confirmAddStudentBtn');

  btn.disabled = true;
  btn.textContent = 'Adding...';

  const res = await fetch(`${API_BASE_URL}/users?search=${studentEmail}&skip=0&limit=1`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Failed to add student: ${error.detail}`);
    btn.disabled = false;
    btn.textContent = 'Add';
    return;
  }

  let memberID = (await res.json())[0].id;

  const res2 = await fetch(`${API_BASE_URL}/users/${memberID}/groups/${AppState.currentGroupId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!res2.ok) {
    const error = await res2.json();
    window.alert(`Error while adding the member to the group: ${error}`);
    return;
  }

  closeAllAdminModals();
  btn.disabled = false;
  btn.textContent = 'Add Student';
  loadStudents();
});

document.getElementById('btnPostAnnouncement').addEventListener('click', async () => {
  const title = document.getElementById('announcementTitle').value.trim();
  const message = document.getElementById('announcementText').value.trim();
  const isUrgent = document.getElementById('announcementUrgent').checked;
  const btn = document.getElementById('btnPostAnnouncement');

  if (!title || !message) return alert('Please write a title and a message.');
  if (!AppState.currentGroupId) return alert('Please select a group first.');

  btn.disabled = true;
  btn.textContent = 'Posting...';

  const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/announcement`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      title: title,
      content: message,
      urgent: isUrgent,
    }),
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while creating new annoucement: ${error}`);
    return;
  }

  document.getElementById('announcementTitle').value = '';
  document.getElementById('announcementText').value = '';
  document.getElementById('announcementUrgent').checked = false;

  btn.disabled = false;
  btn.textContent = 'Post to Class';

  alert('Announcement posted successfully!');
});

document.getElementById('confirmUpdateTimetableBtn').addEventListener('click', async () => {
  const fileInput = document.getElementById('timetableFile').files[0];
  if (!fileInput) return alert('Please select a .ics file.');
  const btn = document.getElementById('confirmUpdateTimetableBtn');

  btn.disabled = true;
  btn.textContent = 'Uploading...';

  const formData = new FormData();
  formData.append('file', fileInput);

  const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/schedules`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while uploading new schedule: ${error}`);
    return;
  }

  closeAllAdminModals();
  btn.disabled = false;
  btn.textContent = 'Upload';
});

document.getElementById('confirmAddEventBtn').addEventListener('click', async () => {
  const title = document.getElementById('eventTitle').value.trim();
  const description = document.getElementById(`eventDescription`).value.trim();
  document.getElementById(`eventDescription`).value = '';
  const location = document.getElementById('eventLocation').value.trim();
  const type = document.getElementById('eventType').value;
  const start = document.getElementById('eventStart').value;
  const end = document.getElementById('eventEnd').value;
  const btn = document.getElementById('confirmAddEventBtn');

  if (!title || !start || !end) return alert('Please fill in title, start, and end times.');

  btn.disabled = true;
  btn.textContent = 'Creating...';

  const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/events`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      title: title,
      description: description,
      start: new Date(start).toISOString(),
      end: new Date(end).toISOString(),
      type: type,
      location: location,
    }),
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while creating new event: ${error}`);
    return;
  }

  closeAllAdminModals();
  btn.disabled = false;
  btn.textContent = 'Create Event';
});

document.getElementById('confirmStartElectionBtn').addEventListener('click', async () => {
  const title = document.getElementById('electionTitle').value.trim();
  const optionsRaw = document.getElementById('electionOptions').value.trim();
  const btn = document.getElementById('confirmStartElectionBtn');

  if (!title || !optionsRaw) return alert('Please fill in the title and options.');
  const optionsArray = optionsRaw
    .split(',')
    .map((opt) => opt.trim())
    .filter((opt) => opt.length > 0);

  btn.disabled = true;
  btn.textContent = 'Starting...';

  let res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/polls`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      title: title,
    }),
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while creating new poll: ${error}`);
    return;
  }

  let pollData = await res.json();
  let pollID = pollData.id;

  optionsArray.forEach(async (option) => {
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
      window.alert(`Error while adding new option: ${error}`);
      return;
    }
  });

  closeAllAdminModals();
  btn.disabled = false;
  btn.textContent = 'Start';
});

async function promoteToDelegate(studentId, isPromoting) {
  const actionText = isPromoting ? 'promote this student to Delegate' : 'remove Delegate status';
  if (!confirm(`Are you sure you want to ${actionText}?`)) return;

  const newRole = isPromoting ? 'delegate' : 'student';
  const res = await fetch(`${API_BASE_URL}/users/${studentId}/role?role=${newRole}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while changing role: ${error}`);
    return;
  }

  loadStudents();
}

async function kickStudent(studentId) {
  if (!confirm('Are you sure you want to kick this student from the group?')) return;

  const res = await fetch(`${API_BASE_URL}/users/${studentId}/groups/${AppState.currentGroupId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });
  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while kicking user: ${error}`);
    return;
  }

  loadStudents();
}

document.addEventListener('groupChanged', () => {
  loadStudents();
});

if (AppState.currentGroupId) {
  setTimeout(loadStudents, 100);
}

loadAdminData();
