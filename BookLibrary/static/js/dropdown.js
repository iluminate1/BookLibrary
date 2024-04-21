const dropdownBtn = document.querySelector('.profile__inner')
const dropdownMenu = document.querySelector('.profile__dropdown')
const arrowSvg = document.querySelector('#arrow')

const toggleDropdown = () => {
    dropdownMenu.classList.toggle('show');
    arrowSvg.classList.toggle('arrow')
}

dropdownBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleDropdown();
})

document.documentElement.addEventListener('click', () => {
    if (dropdownMenu.classList.contains('show')) {
        toggleDropdown();
    }
})