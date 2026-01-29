from flask import Flask, request, jsonify, render_template
from sport_rules import SPORT_RULES

def analyze_with_rules(text, age=None, gender=None):
    """
    Правило-ориентированный анализ текста на основе SPORT_RULES
    """
    text_lower = text.lower()
    scores = {}
    
    # Подсчёт совпадений по ключевым словам
    for sport, rule in SPORT_RULES.items():
        matches = 0
        for keyword in rule["keywords"]:
            if keyword in text_lower:
                matches += 1
        
        # Применяем фильтр по возрасту
        if age is not None and age < rule.get("min_age", 0):
            matches = 0  # Исключаем, если слишком молод
        
        scores[sport] = matches
    
    # Находим лучший результат
    best_sport = max(scores, key=scores.get)
    best_score = scores[best_sport]
    
    if best_score == 0:
        return {
            "sport": "Универсальный спорт (например, плавание)",
            "confidence": 60,
            "reason": "Не удалось определить чёткий психологический профиль. Рекомендуем начать с универсальных видов спорта."
        }
    
    # Расчёт уверенности (макс. ~100%)
    confidence = min(95, int(best_score / len(SPORT_RULES[best_sport]["keywords"]) * 120))
    
    # Формируем объяснение
    reason = SPORT_RULES[best_sport]["reason"]
    if age is not None and gender:
        reason += f" {SPORT_RULES[best_sport]['gender_notes'].get(gender, '')}"
    
    return {
        "sport": best_sport,
        "confidence": confidence,
        "reason": reason
    }

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('Main_page.html')

@app.route('/analyze')
def analyze_page():
    return render_template('SignSport-2.0.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Неверный формат данных"}), 400
    
    text = data.get('text', '').strip()
    age = data.get('age')
    gender = data.get('gender')
    
    # Валидация возраста
    try:
        age = int(age) if age else None
        if age is not None and (age < 5 or age > 100):
            return jsonify({"error": "Возраст должен быть от 5 до 100 лет"}), 400
    except (ValueError, TypeError):
        age = None
    
    if not text:
        return jsonify({"error": "Пожалуйста, введите описание характера."}), 400
    
    result = analyze_with_rules(text, age=age, gender=gender)
    return jsonify(result)

@app.errorhandler(404)
def page_not_found(e):
    return "Страница не найдена", 404

if __name__ == '__main__':
    app.run(debug=True)