document.addEventListener('DOMContentLoaded', function () {
    // 🔑 КЛЮЧЕВАЯ ПРОВЕРКА: только на странице анализа
    if (window.location.pathname !== '/analyze') {
        return;
    }

    const inputField = document.getElementById('reportInput');
    if (!inputField) return;

    const modal = document.getElementById('warningModal');
    const acceptBtn = document.getElementById('acceptBtn');
    const declineBtn = document.getElementById('declineBtn');

    // Блокируем форму
    inputField.disabled = true;
    const analyzeBtn = document.querySelector('.analyze-button');
    if (analyzeBtn) analyzeBtn.disabled = true;

    // Показываем модалку
    if (modal) modal.style.display = 'block';

    // Обработка "Да"
    if (acceptBtn) {
        acceptBtn.addEventListener('click', function () {
            if (modal) modal.style.display = 'none';
            inputField.disabled = false;
            if (analyzeBtn) analyzeBtn.disabled = false;
        });
    }

    // Обработка "Нет"
    if (declineBtn) {
        declineBtn.addEventListener('click', function () {
            const goodbye = document.getElementById('goodbyeScreen');
            if (goodbye) {
                document.body.innerHTML = '';
                document.body.style.margin = '0';
                document.body.style.padding = '0';
                document.body.style.overflow = 'hidden';
                document.body.appendChild(goodbye);
            }
        });
    }
});