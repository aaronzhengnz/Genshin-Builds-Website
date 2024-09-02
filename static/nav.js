const stackMenu = document.querySelector('.stack-menu');
const hiddenMenu = document.querySelector('.hidden-menu');

console.log(stackMenu); // Should log the stackMenu element
console.log(hiddenMenu); // Should log the hiddenMenu element

stackMenu.addEventListener('click', () => {
  stackMenu.classList.toggle('active');
  hiddenMenu.classList.toggle('active');
});
