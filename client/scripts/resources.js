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
const resourceTemplate = document.getElementById('resourceCardTemplate');
const categoryTemplate = document.getElementById('categoryTemplate');
const resourcesContainer = document.getElementById('resourcesList');
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
    await uploadResource();
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Upload';
});

function formatMessageTime(rawDateString) {
    if (!rawDateString) return '';

    let safeString = rawDateString.replace(' ', 'T');

    if (!safeString.endsWith('Z') && !safeString.includes('+')) {
        safeString += 'Z';
    }

    const date = new Date(safeString);

    if (isNaN(date.getTime())) return '';

    const timeStr = date.toLocaleTimeString('en-GB', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });

    const dateStr = date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });

    return `${timeStr} - ${dateStr}`;
}

async function deleteResource(id) {
    try {
        const res = await fetch(`${API_BASE_URL}/resources/${id}`, {
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
            loadResources();
        }

    } catch (error) {
        console.error("Failed to delete resource :", error.message);
    }
}

async function loadResources() {
    if (!AppState.currentGroupId) return;

    resourcesContainer.innerHTML = '';

    const res = await fetch(`${API_BASE_URL}/groups/${AppState.currentGroupId}/resources`, {
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
            let resourceId = element.id;
            let title = element.title;
            let name = element.uploader.first_name + ' ' + element.uploader.last_name;
            let category = element.category;
            let date = element.uploaded_at;

            addResource(resourceId, title, name, category, date);
        });
    }
}

function addResource(resourceId, title, name, category, date) {
    let categorySection = document.getElementById(`category-${category}`);

    if (!categorySection) {
        categorySection = categoryTemplate.content.cloneNode(true).firstElementChild;
        categorySection.id = `category-${category}`;

        categorySection.querySelector('.category-name').textContent = CATEGORY_CONFIG[category].title;
        categorySection.querySelector('.category-icon').textContent = CATEGORY_CONFIG[category].icon;

        resourcesContainer.appendChild(categorySection);
    }

    const resourceNode = resourceTemplate.content.cloneNode(true).firstElementChild;
    const iconSpan = resourceNode.querySelector('.file-icon .material-icons-outlined');

    iconSpan.textContent = CATEGORY_CONFIG[category].icon;
    resourceNode.querySelector('.file-icon').style.color = CATEGORY_CONFIG[category].color;
    resourceNode.querySelector('.file-name').textContent = title;
    resourceNode.querySelector('.file-meta').innerHTML = `${name} <br> ${formatMessageTime(date)}`;

    const downloadBtn = resourceNode.querySelector('.download-btn');
    downloadBtn.value = `${API_BASE_URL}/resources/${resourceId}/download`;

    downloadBtn.addEventListener('click', function () {
        downloadFile(this, title);
    });

    const deleteBtn = resourceNode.querySelector('.delete-btn');
    if (AppState.userProfile.role == "student") {
        deleteBtn.style.display = "none";
    }
    else {
        deleteBtn.value = resourceId;

        deleteBtn.addEventListener('click', function () {
            deleteResource(this.value);
        });
    }


    const filesGrid = categorySection.querySelector('.files-grid');
    filesGrid.appendChild(resourceNode);
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
            displayError(`${error.detail}`);
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
        displayError(`Failed to download the file: ${error}`);
    } finally {
        icon.textContent = 'download';
        btn.disabled = false;
    }
}

async function uploadResource() {
    if (!AppState.currentGroupId) return;

    const file = formFile.files[0];
    if (!file) {
        displayError('Please select a file first');
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
            displayError(`${error.detail}`);
            return;
        }

        const data = await res.json();

        formTitle.value = '';

        if (AppState.userProfile.role === 'student' || AppState.userProfile.role === 'delegate') {
            formCategory.value = 'student';
        } else {
            formCategory.value = 'lecture';
        }

        formFile.value = '';
        uploadModal.classList.remove('active');

        let resourceId = data.id;
        let title = data.title;
        let name = data.uploader.first_name + ' ' + data.uploader.last_name;
        let categoryLabel = data.category;

        addResource(resourceId, title, name, categoryLabel, new Date().toISOString());
    } catch (error) {
        displayError(`Netwotk error: ${error}`);
    }
}

document.addEventListener('groupChanged', () => {
    loadResources();
});

async function initResources() {
    await requireAuth();

    if (AppState.userProfile && AppState.userProfile.role === 'student' || AppState.userProfile.role === 'delegate') {
        formCategory.value = 'student';
        formCategory.disabled = true;
    }

    if (AppState.currentGroupId) {
        await loadResources();
    }
}

initResources()
