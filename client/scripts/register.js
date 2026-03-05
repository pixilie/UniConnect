async function register(firstName,lastName,email,password){
    try{
        const res = await fetch("http://localhost:3000/api/register", {
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