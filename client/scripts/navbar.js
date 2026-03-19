const profileName = document.getElementById("currentUserName");
const profileAvatar = document.getElementById("currentUserAvatar");
const profileRole = document.getElementById("currentUserRole");
const groupList = document.getElementById("groupList");

const AppState = {
    currentGroupId: localStorage.getItem("groupID") || null,
    currentGroupName: "",
    userProfile: null
};

async function getProfileData() {
    const token = localStorage.getItem("token");
    if (!token) return;

    const res = await fetch(`${API_BASE_URL}/users/me`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!res.ok) {
        console.error("Issue with getting profile data");
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
    if (profileData.role === "student") {
        groupList.disabled = true;
    }

    groupList.innerHTML = "";

    for (const group of profileData.groups) {
        const option = new Option(group.name, group.id);
        option.className+=" groupOption";
        groupList.add(option);
    }

    if (!AppState.currentGroupId && profileData.groups.length > 0) {
        AppState.currentGroupId = profileData.groups[0].id;
        localStorage.setItem("groupID", AppState.currentGroupId);
    }

    if (AppState.currentGroupId) {
        groupList.value = AppState.currentGroupId;
    }
}

groupList.addEventListener("change", function (event) {
    const newGroupId = event.target.value;
    console.log(`New group selected: ${newGroupId}`);

    localStorage.setItem("groupID", newGroupId);
    AppState.currentGroupId = newGroupId;

    const groupChangeEvent = new CustomEvent("groupChanged", {
        detail: { newId: newGroupId }
    });
    document.dispatchEvent(groupChangeEvent);
});

getProfileData();
