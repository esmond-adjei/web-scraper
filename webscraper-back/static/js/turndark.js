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
function myFunction() {
  // Get the text field
  var copyText = document.getElementById("myInput");

  // Select the text field
  copyText.select();
  // copyText.setSelectionRange(0, 99999); // For mobile devices

   // Copy the text inside the text field
  navigator.clipboard.writeText(copyText.value);

  // Alert the copied text
  alert("Copied!");
}