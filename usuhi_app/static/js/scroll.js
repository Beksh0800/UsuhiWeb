document.addEventListener("DOMContentLoaded", function () {
        // Обработчики для кнопок прокрутки
        const scrollButtons = document.querySelectorAll('.scroll-button');

        scrollButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetSelector = button.getAttribute('data-target');
                const row = document.querySelector(targetSelector);
                if (!row) {
                    return;
                }
                const direction = button.classList.contains('prev') ? -1 : 1;
                const scrollAmount = row.clientWidth * 0.3; // Scroll by 30% of the visible area
                row.scrollBy({ left: direction * scrollAmount, behavior: 'smooth' });
            });
        });

        const rowElements = document.querySelectorAll('.scr .row');

        rowElements.forEach(row => {
            let isDown = false;
            let startX;
            let scrollLeft;

            row.addEventListener('mousedown', (e) => {
                isDown = true;
                row.classList.add('active');
                startX = e.pageX - row.offsetLeft;
                scrollLeft = row.scrollLeft;
            });

            row.addEventListener('mouseleave', () => {
                isDown = false;
                row.classList.remove('active');
            });

            row.addEventListener('mouseup', () => {
                isDown = false;
                row.classList.remove('active');
            });

            row.addEventListener('mousemove', (e) => {
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - row.offsetLeft;
                const walk = (x - startX) * 2; //scroll-fast
                row.scrollLeft = scrollLeft - walk;
            });
        });
    });