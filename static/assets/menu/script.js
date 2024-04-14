document.addEventListener('DOMContentLoaded', () => {
    const menu = document.querySelector('.menu');
    const button = document.querySelector('.menu_toggler');
    const toggleMenu = () => {
        if (window.innerWidth >= 768) {
            menu.style.display = 'block';
        } else {
            if (button.classList.contains('cross')) {
                menu.style.display = 'block';
            } else {
                menu.style.display = 'none';
            }
        }
    };

    toggleMenu();

    button.addEventListener('click', () => {
        if (button.classList.contains('cross')) {
            button.classList.remove('cross');
            button.classList.add('toggle');
            toggleMenu();
        } else {
            button.classList.remove('toggle');
            button.classList.add('cross');
            toggleMenu();
        }
    });

    window.addEventListener('resize', toggleMenu);
});
