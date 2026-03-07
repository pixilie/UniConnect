async function login(username, password) {
  const params = new URLSearchParams();
  params.append("grant_type", "password");
  params.append("username", username);
  params.append("password", password);

  try {
    const res = await fetch("https://uniconnect.pixilie.net/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params
    });

    if (!res.ok) return false;

    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    return true;

  } catch (err) {
    console.log(err);
    return false;
  }
}

document.getElementById("loginForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;

  let message = document.getElementById("message");
  let success = await login(email, password);

  if (success) {
    message.style.color = "green";
    message.innerText = "Login Successful!";
    window.location.href = "chat.html";
  }
  else {
    message.style.color = "red";
    message.innerText = "Invalid email or password";
  }

});
