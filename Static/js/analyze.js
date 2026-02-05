document.addEventListener('DOMContentLoaded', function () {
    if (window.location.pathname !== '/analyze') return;

    const declineBtn = document.getElementById('declineBtn');
    const acceptBtn = document.getElementById('acceptBtn');
    const modal = document.getElementById('warningModal');
    const inputField = document.getElementById('reportInput');
    const analyzeBtn = document.querySelector('.analyze-button');

    // Отладка: проверим, что элементы найдены
    console.log("Элементы:", { declineBtn, acceptBtn, modal, inputField, analyzeBtn });

    if (!modal || !inputField) return;

    // Блокируем
    inputField.disabled = true;
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        console.log("Кнопка анализа ЗАБЛОКИРОВАНА");
    }
    modal.style.display = 'block';

    // Обработка "Да"
    if (acceptBtn) {
        acceptBtn.addEventListener('click', () => {
            console.log("Нажата кнопка 'Да'");
            modal.style.display = 'none';
            inputField.disabled = false;
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                console.log("Кнопка анализа РАЗБЛОКИРОВАНА");
            }
        });
    } else {
        console.error("❌ Кнопка #acceptBtn не найдена!");
    }

    // Обработка "Нет"
    if (declineBtn) {
        declineBtn.addEventListener('click', () => {
            window.location.href = '/goodbye';
        });
    }
});

// Дополнительно: убедимся, что runAnalysis вызывается
function runAnalysis() {
    console.log("Запуск анализа...");
    const text = document.getElementById('reportInput').value.trim();
    if (!text) {
        alert("Пожалуйста, введите описание характера");
        return;
    }

    fetch('/api/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text})
    })
    .then(response => {
        console.log("Ответ от сервера:", response.status);
        return response.json();
    })
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById('recommendedSport').textContent = data.sport;
            document.getElementById('confidence').textContent = data.confidence;
            document.getElementById('result').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Не удалось подключиться к серверу.');
    });
}