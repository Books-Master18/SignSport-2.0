function runAnalysis() {
    const text = document.getElementById('reportInput').value;
    const age = document.getElementById('age').value || null;
    const gender = document.getElementById('gender').value || null;
    
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
    });
}