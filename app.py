from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('Main_page.html')

@app.route('/analyze')
def analyze_page():
    return render_template('SignSport-2.0.html')

@app.errorhandler(404)
def page_not_found(e):
    return "Страница не найдена", 404

if __name__ == '__main__':
    app.run(debug=True)