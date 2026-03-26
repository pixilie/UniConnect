requireAuth();

const CATEGORY_CONFIG = {
    "lecture": {
        title: "Lectures & Slides",
        icon: "description",
        color: "#6750A4"
    },
    "exercise": {
        title: "Exercises & Assignments",
        icon: "assignment",
        color: "#1976D2"
    },
    "student": {
        title: "Shared by Students",
        icon: "group",
        color: "#388E3C"
    },
    "other": {
        title: "Other Resources",
        icon: "folder_open",
        color: "#F57C00"
    }
};

const openModalBtn = document.getElementById('openUploadModalBtn');
const uploadModal = document.getElementById('uploadModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelUploadBtn = document.getElementById('cancelUploadBtn');

openModalBtn.addEventListener('click', () => {
    uploadModal.classList.add('active');
});

closeModalBtn.addEventListener('click', () => {
    uploadModal.classList.remove('active');
});

cancelUploadBtn.addEventListener('click', () => {
    uploadModal.classList.remove('active');
});

uploadModal.addEventListener('click', (e) => {
    if (e.target === uploadModal) {
        uploadModal.classList.remove('active');
    }
});
