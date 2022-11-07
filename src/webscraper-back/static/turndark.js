const checkbox = document.getElementById("checkbox");

checkbox.addEventListener("change", () => {
  darkTargets = document.querySelectorAll("#turn-dark");
  // console.log(darkTargets);
  for (let i = 0; i < darkTargets.length; i++) {
    darkTargets[i].classList.toggle("dark");
  }
});