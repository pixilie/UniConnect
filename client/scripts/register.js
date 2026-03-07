async function register(firstName, lastName, email, password) {
  try {
    const res = await fetch("https://uniconnect.pixilie.net/api/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password
      })
    })
    if (!res.ok) return false;
    return true;
  } catch (err) {
    return false;
  }
}

async function tryRegister() {
  fullName = document.getElementById("fullname").textContent;
  email = document.getElementById("email").textContent;
  password = document.getElementById("password").textContent;

  names = fullName.split(" ");
  firstName = names[0];
  names.shift();
  lastName = names.join(" ")

  success = await register(firstName, lastName, email, password);

  if (success) window.location.href = 'chat.html';
  else alert("registration failed");
}
