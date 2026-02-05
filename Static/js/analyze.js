// SignSport — Полный клиентский код с модальным окном и альтернативными рекомендациями

document.addEventListener('DOMContentLoaded', function () {
    // Работаем только на странице анализа
    if (!window.location.pathname.startsWith('/analyze')) return;

    const modal = document.getElementById('warningModal');
    const inputField = document.getElementById('reportInput');
    const analyzeBtn = document.querySelector('.analyze-button');
    const declineBtn = document.getElementById('declineBtn');
    const acceptBtn = document.getElementById('acceptBtn');

    if (!modal || !inputField) return;

    // Блокируем интерфейс до подтверждения
    inputField.disabled = true;
    if (analyzeBtn) analyzeBtn.disabled = true;
    modal.style.display = 'flex'; // или 'block'

    // Подтверждение
    acceptBtn?.addEventListener('click', () => {
        modal.style.display = 'none';
        inputField.disabled = false;
        if (analyzeBtn) analyzeBtn.disabled = false;
    });

    // Отказ
    declineBtn?.addEventListener('click', () => {
        window.location.href = '/goodbye';
    });
});

// Основная функция анализа — с поддержкой альтернатив
async function runAnalysis() {
    const text = document.getElementById("reportInput")?.value?.trim();
    const btn = document.querySelector(".analyze-button");
    const resultDiv = document.getElementById("result");

    if (!text) {
        alert("Пожалуйста, введите описание характера");
        return;
    }

    const originalBtnText = btn?.textContent || "Анализировать";
    if (btn) {
        btn.disabled = true;
        btn.textContent = "Анализ...";
    }

    resultDiv.style.display = "none";
    resultDiv.innerHTML = "";
    resultDiv.style.opacity = "0";

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        let resultHTML = `
            <div class="result-header">
                <span class="checkmark">✅</span>
                <strong>Рекомендация готова!</strong>
            </div>
            <div class="result-container">
                <h3>🎯 Основная рекомендация:</h3>
                <div class="main-recommendation">
                    <div class="sport-name">${data.sport}</div>
                    <div class="confidence">Уверенность: ${data.confidence}%</div>
                    <div class="reason">${data.reason || ""}</div>
                </div>
        `;

        // 🔥 Добавляем альтернативные варианты, если они есть
        if (data.additional_recommendations && data.additional_recommendations.length > 0) {
            resultHTML += `
                <div class="alternative-recommendations">
                    <h4>🔄 Альтернативные варианты:</h4>
                    <div class="alternatives-list">
            `;
            data.additional_recommendations.forEach((rec, index) => {
                resultHTML += `
                    <div class="alternative-item">
                        <span class="alt-sport">${index + 1}. ${rec.sport}</span>
                        <span class="alt-confidence">${rec.confidence}%</span>
                    </div>
                `;
            });
            resultHTML += `
                    </div>
                </div>
            `;
        }

        resultHTML += `</div>`;
        resultDiv.innerHTML = resultHTML;
        resultDiv.style.display = "block";

        // Плавное появление
        setTimeout(() => {
            resultDiv.style.transition = "opacity 0.5s ease";
            resultDiv.style.opacity = "1";
        }, 50);

    } catch (error) {
        console.error("Ошибка запроса:", error);
        resultDiv.innerHTML = `
            <div class="result-header">
                <span style="font-size: 24px; margin-right: 10px;">⚠️</span>
                <strong>Ошибка подключения</strong>
            </div>
            <div class="error-message">
                <p style="color: #c0392b; padding: 15px; background: #f8d7da; border-radius: 5px; margin: 15px 0;">
                    ❌ Не удалось подключиться к серверу. Убедитесь, что он запущен.
                </p>
            </div>
        `;
        resultDiv.style.display = "block";
        resultDiv.style.opacity = "1";
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = originalBtnText;
        }
    }
}