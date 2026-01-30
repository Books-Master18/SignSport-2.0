function runAnalysis() {
    const text = document.getElementById('reportInput').value.trim();
    const ageStr = document.getElementById('age').value;
    const gender = document.getElementById('gender').value || null;

    // Преобразуем возраст в число или null
    const age = ageStr ? parseInt(ageStr, 10) : null;

    if (!text) {
        alert("Пожалуйста, введите описание характера");
        return;
    }

    fetch('/api/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text, age, gender})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById('recommendedSport').textContent = data.sport;
            document.getElementById('confidence').textContent = data.confidence;
            document.getElementById('reasonText').textContent = data.reason;
            document.getElementById('result').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Не удалось подключиться к серверу.');
    });
}