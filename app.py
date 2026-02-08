from flask import Flask, request, jsonify, render_template
import re
from sport_rules import SPORT_RULES
from config import PROJECT_PROGRESS
import pymorphy3
from synonyms import SYNONYM_GROUPS

# === Инициализация ===
morph = pymorphy3.MorphAnalyzer()

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def normalize_phrase(phrase):
    """Превращает фразу в множество лемм."""
    words = re.findall(r'[а-яё]+', phrase.lower())
    lemmas = set()
    for word in words:
        parsed = morph.parse(word)
        if parsed:
            lemma = parsed[0].normal_form
            lemmas.add(lemma)
    return lemmas

# === Предварительная обработка синонимов ===
NORMALIZED_SYNONYMS = {}
for concept, phrases in SYNONYM_GROUPS.items():
    normalized_phrases = []
    for phrase in phrases:
        normalized_phrases.append(normalize_phrase(phrase))
    NORMALIZED_SYNONYMS[concept] = normalized_phrases

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

def expand_text_with_synonyms(user_lemmas, normalized_synonyms):
    """Сравнивает леммы пользователя с нормализованными фразами."""
    matched_concepts = set()
    for concept, phrase_lemmas_list in normalized_synonyms.items():
        for phrase_lemmas in phrase_lemmas_list:
            if phrase_lemmas.issubset(user_lemmas):
                matched_concepts.add(concept)
                break
    return matched_concepts

# === Анализ текста ===
def analyze_with_rules(text):
    if not is_meaningful_text(text):
        return {"error": "Текст слишком короткий или не содержит описания характера."}

    user_lemmas = lemmatize_text_to_set(text)
    user_concepts = expand_text_with_synonyms(user_lemmas, NORMALIZED_SYNONYMS)

    # 1. Считаем базовые баллы
    scores = {}
    for sport, rule in SPORT_RULES.items():
        total_weight = 0
        keywords = rule.get("keywords", {})
        for concept, weight in keywords.items():
            if concept in user_concepts:
                total_weight += weight
        scores[sport] = total_weight

    # 2. Применяем НЕГАТИВНЫЕ МАРКЕРЫ (если есть)
    if "потребность_в_одобрении" in user_concepts:
        scores["Плавание🏊"] = max(0, scores.get("Плавание🏊", 0) - 15)

    # 3. Сортируем по убыванию баллов (для последующего расчёта)
    sorted_sports = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # === НОВАЯ ЛОГИКА: формируем рекомендации с confidence и сортируем по ней ===
    all_recommendations = []
    for sport, score in sorted_sports:
        if score <= 0:
            continue
        rule = SPORT_RULES[sport]
        keywords = rule.get("keywords", {})
        max_possible = sum(keywords.values()) if keywords else 1
        # Рассчитываем уверенность как процент от максимума
        conf = min(95, max(50, int((score / max_possible) * 100)))
        reason = rule.get("reason", "")
        all_recommendations.append({
            "sport": sport,
            "confidence": conf,
            "reason": reason
        })

    # Если нет подходящих видов
    if not all_recommendations:
        return {
            "sport": "Универсальный спорт (например, плавание)",
            "confidence": 60,
            "reason": "Описание характера не содержит явных признаков, подходящих под конкретный вид спорта.",
            "additional_recommendations": []
        }

    # 🔥 СОРТИРУЕМ ПО УВЕРЕННОСТИ (confidence)!
    all_recommendations.sort(key=lambda x: x["confidence"], reverse=True)

    main = all_recommendations[0]
    alternatives = all_recommendations[1:3]

    return {
        "sport": main["sport"],
        "confidence": main["confidence"],
        "reason": main["reason"],
        "additional_recommendations": [
            {"sport": alt["sport"], "confidence": alt["confidence"]}
            for alt in alternatives
        ]
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

    try:
        result = analyze_with_rules(text)
    except Exception as e:
        return jsonify({"error": f"Ошибка анализа: {str(e)}"}), 500

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)



@app.errorhandler(404)
def page_not_found(e):
    return "Страница не найдена", 404

if __name__ == '__main__':
    import os
    # Определяем, запущено ли приложение на Render
    is_render = os.environ.get('RENDER') is not None

    if is_render:
        # На Render: без debug, свой порт
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Локально: с debug, стандартный порт
        app.run(debug=True, host='127.0.0.1', port=5000)
    