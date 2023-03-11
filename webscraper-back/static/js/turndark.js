const checkbox = document.getElementById("checkbox");
const DARK_THEME_KEY = "dark-theme-enabled";

// Check if the user had previously enabled the dark theme
const isDarkThemeEnabled = localStorage.getItem(DARK_THEME_KEY) === "true";
if (isDarkThemeEnabled) {
  enableDarkTheme();
  checkbox.checked = true;
}

// Add event listener for the checkbox
checkbox.addEventListener("change", () => {
  if (checkbox.checked) {
    enableDarkTheme();
    localStorage.setItem(DARK_THEME_KEY, "true");
  } else {
    disableDarkTheme();
    localStorage.removeItem(DARK_THEME_KEY);
  }
});

function enableDarkTheme() {
  darkTargets = document.querySelectorAll("#turn-dark");
  for (let i = 0; i < darkTargets.length; i++) {
    darkTargets[i].classList.add("dark");
  }
}

function disableDarkTheme() {
  darkTargets = document.querySelectorAll("#turn-dark");
  for (let i = 0; i < darkTargets.length; i++) {
    darkTargets[i].classList.remove("dark");
  }
}


// --------------------------------------------------
function copy(movieLink) {
  navigator.clipboard.writeText(movieLink);
  alert("Copied to clipboard!");
}

// --------------------------------------------------
function confirmDel(somevalue){
  document.getElementById("confirm-dialog").style.display = "flex";
  document.getElementById("confirm-button").href = `/delete/${somevalue}`;

  document.querySelector(".get-link-page").style.overflow = 'hidden';
  document.getElementById("confirm-message").innerHTML = `confirm the deletion of <u>${somevalue}</u>`.toUpperCase()
}

function cancelDel(){
  dialog = document.getElementById("confirm-dialog").style.display = "none";
  document.querySelector(".get-link-page").style.overflow = 'auto';
}

function flushMessage(){
  dialog = document.getElementById("confirm-dialog").style.display = "flex";
  clear_dialog = document.querySelectorAll(".flush");
  console.log(clear_dialog.length)
  for(var i = 0; i< clear_dialog.length; i++){
    console.log(clear_dialog[i]);
    clear_dialog[i].style.display = "none";
  }

  document.getElementById("confirm-dialog").innerHTML = `
      <div class="success" style="display:flex; justify-content:center;">
          <img
            src="/static/images/saved-png.png"
            alt="saved successfully"
            width="150"
            height="150"
          />
      </div>`;
}