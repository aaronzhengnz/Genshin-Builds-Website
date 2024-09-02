const stackMenu = document.querySelector('.stack-menu');
const hiddenMenu = document.querySelector('.hidden-menu');

stackMenu.addEventListener('click', () => {
  stackMenu.classList.toggle('active');
  hiddenMenu.classList.toggle('active');
});