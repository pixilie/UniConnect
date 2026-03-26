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

const uploadBtn= document.getElementById("confirmUploadBtn");
const openModalBtn = document.getElementById('openUploadModalBtn');
const uploadModal = document.getElementById('uploadModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelUploadBtn = document.getElementById('cancelUploadBtn');
const ressourceTemplate=document.getElementById(`resourceCardTemplate`);
const categoryTemplate=document.getElementById(`categoryTemplate`);
const ressourcesContainer=document.getElementById(`resourcesList`);

const formTitle=document.getElementById("uploadTitle");
const formCategory=document.getElementById("uploadCategory");
const formFile=document.getElementById("uploadFile");

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

uploadBtn.addEventListener(`click`, ()=>{
    uploadRessource();
    uploadModal.classList.remove('active');
})

async function loadRessources() {
    const currentGroupId = AppState.currentGroupId;

    if (!currentGroupId) return;

    ressourcesContainer.innerHTML = "";
    const res = await fetch(`${API_BASE_URL}/groups/${currentGroupId}/resources`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });

    if (!res.ok) {
        console.error(`Error while fetching Ressources: ${res.status}`);
    } else {
        let data = await res.json();

        data.forEach(element => {
            let link = element.file_path;
            let title= element.title;
            let name=element.author.first_name+" "+element.author.last_name;
            let category=element.category;

            addRessource(link,title,name,category);
        });
    }
    
}

function addRessource(link,title,name,category){
    const ressourceNode = ressourceTemplate.content.cloneNode(true);
    
    let categoryDiv= document.getElementById(category);
    if(!categoryDiv){
        const categoryDiv= categoryTemplate.content.cloneNode(true);
        categoryDiv.querySelector(`.category-name`).content=CATEGORY_CONFIG[category].title;
        ressourcesContainer.appendChild(categoryDiv);
    }
    ressourceNode.querySelector(`.file-icon`).querySelector(`.material-icons-outlined`).content=CATEGORY_CONFIG[category].icon;
    ressourceNode.querySelector(`.file-icon`).querySelector(`.material-icons-outlined`).style.color=CATEGORY_CONFIG[category].color;
    ressourceNode.querySelector(`.file-name`).content=title;
    ressourceNode.querySelector(`.file-meta`).content=name;
    ressourceNode.querySelector(`.download-btn`).value=link;
    categoryDiv.appendChild(ressourceNode);
}



function downloadFile(btn) {
    const a = document.createElement("a");
    a.href = btn.value;
    a.download = "";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

async function uploadRessource() {
    const file = formFile.files[0];

    if (!file) {
        alert("Select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("title", formTitle.value);
    formData.append("category", category.value);
    formData.append("file", file);
    formTitle.value="";
    formCategory.value="";
    formFile.value="";

    const res = await fetch(`/api/groups/${currentGroupId}/resources`, {
        method: "POST",
        body: formData
    });

    if(!res.ok){
        console.log("issue uploading file");
        return;
    }
    const data = await res.json();

    let link = data.file_path;
    let title= data.title;
    let name=data.author.first_name+" "+data.author.last_name;
    let category=data.category;

    addRessource(link,title,name,category);
}

loadRessources();