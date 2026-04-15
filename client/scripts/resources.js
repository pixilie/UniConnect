requireAuth();

const CATEGORY_CONFIG = {
  lecture: {
    title: 'Lectures & Slides',
    icon: 'description',
    color: '#6750A4',
  },
  exercise: {
    title: 'Exercises & Assignments',
    icon: 'assignment',
    color: '#1976D2',
  },
  student: { title: 'Shared by Students', icon: 'group', color: '#388E3C' },
  other: { title: 'Other Resources', icon: 'folder_open', color: '#F57C00' },
};

const uploadBtn = document.getElementById('confirmUploadBtn');
const openModalBtn = document.getElementById('openUploadModalBtn');
const uploadModal = document.getElementById('uploadModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelUploadBtn = document.getElementById('cancelUploadBtn');
const ressourceTemplate = document.getElementById('resourceCardTemplate');
const categoryTemplate = document.getElementById('categoryTemplate');
const ressourcesContainer = document.getElementById('resourcesList');

const formTitle = document.getElementById('uploadTitle');
const formCategory = document.getElementById('uploadCategory');
const formFile = document.getElementById('uploadFile');

openModalBtn.addEventListener('click', () => uploadModal.classList.add('active'));
closeModalBtn.addEventListener('click', () => uploadModal.classList.remove('active'));
cancelUploadBtn.addEventListener('click', () => uploadModal.classList.remove('active'));

uploadModal.addEventListener('click', (e) => {
  if (e.target === uploadModal) uploadModal.classList.remove('active');
});

uploadBtn.addEventListener('click', async () => {
  uploadBtn.disabled = true;
  uploadBtn.textContent = 'Uploading...';
  await uploadRessource();
  uploadBtn.disabled = false;
  uploadBtn.textContent = 'Upload';
});

async function loadRessources() {
  if (!AppState.currentGroupId) return;

  ressourcesContainer.innerHTML = '';

  const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/resources`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    window.alert(`Error while fetching ressources: ${error}`);
    return;
  } else {
    let data = await res.json();

    data.forEach((element) => {
      let resourceId = element.id;
      let title = element.title;
      let name = element.uploader.first_name + ' ' + element.uploader.last_name;
      let category = element.category;

      addRessource(resourceId, title, name, category);
    });
  }
}

function addRessource(resourceId, title, name, category) {
  let categorySection = document.getElementById(`category-${category}`);

  if (!categorySection) {
    categorySection = categoryTemplate.content.cloneNode(true).firstElementChild;
    categorySection.id = `category-${category}`;

    categorySection.querySelector('.category-name').textContent = CATEGORY_CONFIG[category].title;
    categorySection.querySelector('.category-icon').textContent = CATEGORY_CONFIG[category].icon;

    ressourcesContainer.appendChild(categorySection);
  }

  const ressourceNode = ressourceTemplate.content.cloneNode(true).firstElementChild;
  const iconSpan = ressourceNode.querySelector('.file-icon .material-icons-outlined');

  iconSpan.textContent = CATEGORY_CONFIG[category].icon;
  ressourceNode.querySelector('.file-icon').style.color = CATEGORY_CONFIG[category].color;
  ressourceNode.querySelector('.file-name').textContent = title;
  ressourceNode.querySelector('.file-meta').textContent = name;

  const downloadBtn = ressourceNode.querySelector('.download-btn');
  downloadBtn.value = `${API_BASE_URL}/resources/${resourceId}/download`;

  downloadBtn.addEventListener('click', function () {
    downloadFile(this, title);
  });

  const filesGrid = categorySection.querySelector('.files-grid');
  filesGrid.appendChild(ressourceNode);
}

async function downloadFile(btn, fileName) {
  if (btn.disabled) return;

  const icon = btn.querySelector('.material-icons-outlined');

  btn.disabled = true;
  icon.textContent = 'hourglass_empty';

  try {
    const res = await fetch(btn.value, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!res.ok) {
      const error = await res.json();
      window.alert(`Failed to download file: ${error}`);
      return;
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();

    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Erreur lors du téléchargement:', error);
    alert('Failed to download the file.');
  } finally {
    icon.textContent = 'download';
    btn.disabled = false;
  }
}

async function uploadRessource() {
  if (!AppState.currentGroupId) return;

  const file = formFile.files[0];
  if (!file) {
    alert('Please select a file first');
    return;
  }

  const formData = new FormData();
  formData.append('title', formTitle.value);
  formData.append('category', formCategory.value);
  formData.append('file', file);

  const token = localStorage.getItem('token');

  try {
    const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/resources`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!res.ok) {
      const error = await res.json();
      window.alert(`Error while uploading ressource: ${error}`);
      return;
    }

    const data = await res.json();

    formTitle.value = '';
    formCategory.value = 'lecture';
    formFile.value = '';
    uploadModal.classList.remove('active');

    let resourceId = data.id;
    let title = data.title;
    let name = data.uploader.first_name + ' ' + data.uploader.last_name;
    let categoryLabel = data.category;

    addRessource(resourceId, title, name, categoryLabel);
  } catch (error) {
    console.error('Network error:', error);
  }
}

document.addEventListener('groupChanged', () => {
  loadRessources();
});

if (AppState.currentGroupId) {
  setTimeout(() => {
    loadRessources();
  }, 100);
}
