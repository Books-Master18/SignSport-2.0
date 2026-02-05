document.addEventListener('DOMContentLoaded', function () {
    // Работаем только на странице /analyze
    if (window.location.pathname !== '/analyze') {
        return;
    }

    const declineBtn = document.getElementById('declineBtn');
    const acceptBtn = document.getElementById('acceptBtn');
    const modal = document.getElementById('warningModal');
    const inputField = document.getElementById('reportInput');
    const analyzeBtn = document.querySelector('.analyze-button');

    if (!modal || !inputField) return;

    // Блокируем форму до подтверждения
    inputField.disabled = true;
    if (analyzeBtn) analyzeBtn.disabled = true;
    modal.style.display = 'block';

    // При "Да" — разблокируем
    if (acceptBtn) {
        acceptBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            inputField.disabled = false;
            if (analyzeBtn) analyzeBtn.disabled = false;
        });
    }

    // При "Нет" — переходим на отдельную страницу
    if (declineBtn) {
        declineBtn.addEventListener('click', () => {
            window.location.href = '/goodbye';
        });
    }
});