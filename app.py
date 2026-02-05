from flask import Flask, request, jsonify, render_template
import re
from sport_rules import SPORT_RULES
from config import PROJECT_PROGRESS
import pymorphy3

# === Инициализация ===
morph = pymorphy3.MorphAnalyzer()

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def is_meaningful_text(text):
    """Проверяет, похож ли текст на осмысленное описание характера."""
    if len(text) < 20:
        return False
    russian_words = re.findall(r'[а-яё]{3,}', text.lower())
    return len(russian_words) >= 3

def lemmatize_text_to_set(text):
    """Превращает текст в множество лемм (без пунктуации и регистра)."""
    words = re.findall(r'[а-яё]+', text.lower())
    lemmas = set()
    for word in words:
        parsed = morph.parse(word)
        if parsed:
            lemma = parsed[0].normal_form
            lemmas.add(lemma)
    return lemmas

# === Предварительная обработка базы знаний (один раз при запуске) ===
PREPROCESSED_RULES = {}
for sport, rule in SPORT_RULES.items():
    preprocessed = {}
    for phrase, weight in rule.get("keywords", {}).items():
        is_phrase = " " in phrase
        lemmas = lemmatize_text_to_set(phrase) if not is_phrase else set()
        preprocessed[phrase] = {
            "weight": weight,
            "lemmas": lemmas,
            "is_phrase": is_phrase
        }
    PREPROCESSED_RULES[sport] = preprocessed

def analyze_with_rules(text):
    """
    Анализ с гибридной лемматизацией:
    - Фразы (например, "работает в команде") → поиск подстроки
    - Отдельные слова (например, "спокоен") → поиск по леммам
    """
    if not is_meaningful_text(text):
        return {
            "error": "Введённый текст не содержит осмысленного описания характера. "
                     "Пожалуйста, опишите личностные качества человека"
        }

    text_lower = text.lower()
    user_lemmas = lemmatize_text_to_set(text)
    scores = {}

    for sport, keywords in PREPROCESSED_RULES.items():
        total_weight = 0
        for phrase, data in keywords.items():
            weight = data["weight"]
            if data["is_phrase"]:
                # Фраза: ищем точное совпадение как подстроку
                if phrase in text_lower:
                    total_weight += weight
            else:
                # Слово: ищем по леммам
                if data["lemmas"] & user_lemmas:
                    total_weight += weight
        scores[sport] = total_weight

    best_sport = max(scores, key=scores.get)
    best_score = scores[best_sport]

    if best_score > 0:
        # Максимальный балл для этого вида спорта
        max_possible = sum(
            data["weight"] for data in PREPROCESSED_RULES[best_sport].values()
        )
        confidence = min(95, int((best_score / max_possible) * 120))
        reason = SPORT_RULES[best_sport].get("reason", "")
        return {
            "sport": best_sport,
            "confidence": confidence,
            "reason": reason
        }

    return {
        "sport": "Универсальный спорт (например, плавание)",
        "confidence": 60,
        "reason": "Описание характера не содержит явных признаков..."
    }

# === FLASK-ПРИЛОЖЕНИЕ ===
app = Flask(__name__)

@app.context_processor
def inject_global_vars():
    return {'progress': PROJECT_PROGRESS}

@app.route('/')
def home():
    return render_template('Main_page.html')

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
    if not text:
        return jsonify({"error": "Пожалуйста, введите описание характера."}), 400

    result = analyze_with_rules(text)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

@app.errorhandler(404)
def page_not_found(e):
    return "Страница не найдена", 404

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Сайт SignSport запущен!")
    print("👉 Главная: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)