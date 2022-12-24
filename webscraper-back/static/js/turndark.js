const checkbox = document.getElementById("checkbox");

checkbox.addEventListener("change", () => {
  darkTargets = document.querySelectorAll("#turn-dark");
  localStorage.setItem('dark',this.checked);
  console.log(this.checked);
  for (let i = 0; i < darkTargets.length; i++) {
    darkTargets[i].classList.toggle("dark");
  }
});

// --------------------------------------------------
function copy(movieLink) {
  navigator.clipboard.writeText(movieLink);
  alert("Copied to clipboard!");
}