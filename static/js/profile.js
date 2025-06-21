// Активация вкладок
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function () {
        // Удаляем активный класс у всех вкладок
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        // Добавляем активный класс текущей вкладке
        this.classList.add('active');

        // Скрываем все табы
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
        // Показываем выбранный таб
        const tabId = this.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// Активация аккордеонов
document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', function () {
        const accordion = this.parentElement;
        accordion.classList.toggle('active');
    });
});