const checkbox = document.getElementById('checkbox');

checkbox.addEventListener('change', ()=>{
    document.body.classList.toggle('dark');
    document.getElementById('turn-dark').classList.toggle('dark');
})