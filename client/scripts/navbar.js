const profileName = document.getElementById('currentUserName');
const profileAvatar = document.getElementById('currentUserAvatar');
const profileRole = document.getElementById('currentUserRole');

const btn = document.getElementById('groupSelectorBtn');
const dropdown = document.getElementById('groupDropdown');
const searchInput = document.getElementById('groupSearchInput');
const currentGroupNameLabel = document.getElementById('currentGroupName');

btn.addEventListener('click', () => {
  if (btn.classList.contains('disabled')) return;

  dropdown.classList.toggle('active');
  if (dropdown.classList.contains('active')) {
    searchInput.focus();
  }
});

document.addEventListener('click', (e) => {
  if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
    dropdown.classList.remove('active');
  }
});

searchInput.addEventListener('input', (e) => {
  const filter = e.target.value.toLowerCase();
  const items = dropdown.querySelectorAll('.group-item');

  items.forEach((item) => {
    if (item.textContent.toLowerCase().includes(filter)) {
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
    }
  });
});

async function getProfileData() {
  const token = localStorage.getItem('token');
  if (!token) return;

  const res = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`${error.detail}`);
    return;
  }

  const profileData = await res.json();
  AppState.userProfile = profileData;

  profileName.textContent = `${profileData.first_name} ${profileData.last_name}`;
  profileAvatar.textContent = `${profileData.first_name.charAt(0).toUpperCase()}${profileData.last_name.charAt(0).toUpperCase()}`;
  profileRole.textContent = profileData.role;

  setGroupList(profileData);
}

function setGroupList(profileData) {
  if (profileData.role === 'student') {
    btn.classList.add('disabled');
    btn.style.cursor = 'not-allowed';
    btn.style.opacity = '0.7';
  }

  dropdown.querySelectorAll('.group-item').forEach((e) => e.remove());

  if (!AppState.currentGroupId && profileData.groups.length > 0) {
    AppState.currentGroupId = profileData.groups[0].id.toString();
    localStorage.setItem('groupID', AppState.currentGroupId);
  }

  if (profileData.groups.length === 0) {
    currentGroupNameLabel.textContent = 'No group assigned';
    btn.style.pointerEvents = 'none';
    return;
  }

  for (const group of profileData.groups) {
    const item = document.createElement('div');
    item.className = 'group-item';
    item.textContent = group.name;
    item.dataset.groupId = group.id;

    if (AppState.currentGroupId == group.id) {
      item.classList.add('selected');
      currentGroupNameLabel.textContent = group.name;
      AppState.currentGroupName = group.name;
      updateChatInputPlaceholder(group.name);
    }

    item.addEventListener('click', () => {
      const allItems = dropdown.querySelectorAll('.group-item');
      allItems.forEach((i) => i.classList.remove('selected'));
      item.classList.add('selected');

      currentGroupNameLabel.textContent = group.name;
      updateChatInputPlaceholder(group.name);

      dropdown.classList.remove('active');
      searchInput.value = '';
      allItems.forEach((i) => (i.style.display = 'block'));

      const newGroupId = group.id.toString();
      console.log(`New group selected: ${newGroupId}`);
      localStorage.setItem('groupID', newGroupId);
      AppState.currentGroupId = newGroupId;
      AppState.currentGroupName = group.name;

      const groupChangeEvent = new CustomEvent('groupChanged', {
        detail: { newId: newGroupId },
      });
      document.dispatchEvent(groupChangeEvent);
    });

    dropdown.appendChild(item);
  }
}

function updateChatInputPlaceholder(groupName) {
  const chatInput = document.querySelector('.chat-input');
  if (chatInput) {
    chatInput.placeholder = `Type a message in ${groupName}...`;
  }
}

getProfileData();
