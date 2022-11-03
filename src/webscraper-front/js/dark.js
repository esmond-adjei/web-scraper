const checkbox = document.getElementById('checkbox');

checkbox.addEventListener('change', ()=>{
document.body.classList.toggle('dark');
document.getElementsByTagName('main').classList.toggle('dark');
})