function changeLogInOut() {
  let eLogin = document.getElementById("login")
  let eLogout = document.getElementById("logout")

  if (eLogin.style.display == "block"){
    eLogin.style.display = "none"
  }
  else{
    eLogin.style.display = "block"
  }

  if (eLogout.style.display == "block"){
    eLogout.style.display = "none"
  }
  else{
    eLogout.style.display = "block"
  }
}