from flask import Flask, request, jsonify, render_template
import re
from sport_rules import SPORT_RULES
from config import PROJECT_PROGRESS

# === ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: проверка осмысленности текста ===
def is_meaningful_text(text):
    """
    Проверяет, похож ли текст на осмысленное описание характера.
    Требования:
    - минимум 20 символов
    - минимум 3 русских слова длиной >= 3 букв
    """
    if len(text) < 20:
        return False
    russian_words = re.findall(r'[а-яё]{3,}', text.lower())
    return len(russian_words) >= 3

# === ОСНОВНАЯ ЛОГИКА АНАЛИЗА ===


def analyze_with_rules(text):
    """
    Анализирует текст и возвращает рекомендацию на основе SPORT_RULES (с весами)
    """
    if not is_meaningful_text(text):
        return {
            "error": "Введённый текст не содержит осмысленного описания характера. "
                     "Пожалуйста, опишите личностные качества человека"
        }

    text_lower = text.lower()
    scores = {}

    for sport, rule in SPORT_RULES.items():
        total_weight = 0
        # Проходим по каждому слову и его весу
        for keyword, weight in rule["keywords"].items():
            if keyword in text_lower:
                total_weight += weight
        scores[sport] = total_weight

    best_sport = max(scores, key=scores.get)
    best_score = scores[best_sport]

    if best_score > 0:
        # Максимально возможный балл для этого вида спорта
        max_possible = sum(rule["keywords"].values())
        confidence = min(95, int((best_score / max_possible) * 120))
        reason = SPORT_RULES[best_sport]["reason"]
        return {
            "sport": best_sport,
            "confidence": confidence,
            "reason": reason
        }

    return {
        "sport": "Универсальный спорт (например, плавание)",
        "confidence": 60,
        "reason": "Описание характера не содержит явных признаков, связанных с конкретными видами спорта. "
                  "Рекомендуем начать с универсальных видов, таких как плавание или лёгкая атлетика."
    }

# === FLASK-ПРИЛОЖЕНИЕ ===
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('Main_page.html', progress=PROJECT_PROGRESS)

@app.route('/analyze')
def analyze_page():
    return render_template('SignSport-2.0.html')

@app.route('/goodbye')
def goodbye():
    return render_template('goodbye.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Неверный формат данных"}), 400

    text = data.get('text', '').strip()
   # age = data.get('age')
  #  gender = data.get('gender')

    if not text:
        return jsonify({"error": "Пожалуйста, введите описание характера."}), 400

    # Валидация возраста
   # try:
   #     age = int(age) if age else None
   #     if age is not None and (age < 5 or age > 100):
   #         return jsonify({"error": "Возраст должен быть от 5 до 100 лет"}), 400
   # except (ValueError, TypeError):
  #      age = None

  #  result = analyze_with_rules(text, age=age, gender=gender)
    result = analyze_with_rules(text)

    # Если функция вернула ошибку — отправляем её
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

@app.errorhandler(404)
def page_not_found(e):
    return "Страница не найдена", 404


#запуск программы
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Сайт SignSport запущен!")
    print("👉 Главная: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)