from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import random
import os

app = Flask(__name__)
app.secret_key = 'chiave_segreta_progetto_ia'

# Configurazione Database SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELLO DATABASE ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    score = db.Column(db.Integer, default=0)

# --- DATI DEL QUIZ (10 Domande sullo Sviluppo AI) ---
quiz_data = [
    {"q": "Cos'è il Machine Learning?", "a": ["Apprendimento automatico dai dati", "Un linguaggio di programmazione", "Un tipo di hardware", "Un robot antropomorfo"], "c": "Apprendimento automatico dai dati"},
    {"q": "Quale linguaggio è il più usato per l'IA?", "a": ["Python", "C++", "HTML", "PHP"], "c": "Python"},
    {"q": "Cos'è una Rete Neurale?", "a": ["Modello matematico ispirato al cervello", "Una connessione internet veloce", "Un social network per scienziati", "Un database di immagini"], "c": "Modello matematico ispirato al cervello"},
    {"q": "Cosa significa NLP?", "a": ["Natural Language Processing", "New Logic Programming", "Network Layer Protocol", "Non-Linear Programming"], "c": "Natural Language Processing"},
    {"q": "Qual è lo scopo del Test di Turing?", "a": ["Valutare l'intelligenza di una macchina", "Misurare la velocità di calcolo", "Testare la batteria di un PC", "Verificare la sicurezza di un sito"], "c": "Valutare l'intelligenza di una macchina"},
    {"q": "Cos'è il 'Deep Learning'?", "a": ["Sottocampo del ML basato su più strati", "Apprendimento veloce", "Un archivio dati profondo", "Un sensore di profondità"], "c": "Sottocampo del ML basato su più strati"},
    {"q": "A cosa serve la libreria Pandas?", "a": ["Manipolazione e analisi dati", "Creare videogiochi", "Disegnare loghi", "Gestire server web"], "c": "Manipolazione e analisi dati"},
    {"q": "Cos'è il 'Big Data'?", "a": ["Grandi volumi di dati complessi", "Un computer gigante", "Un file molto pesante", "Una connessione satellitare"], "c": "Grandi volumi di dati complessi"},
    {"q": "Chi è considerato uno dei padri dell'IA?", "a": ["Alan Turing", "Steve Jobs", "Mark Zuckerberg", "Bill Gates"], "c": "Alan Turing"},
    {"q": "Cosa fa un algoritmo di classificazione?", "a": ["Assegna etichette a input dati", "Somma numeri casuali", "Formatta il disco rigido", "Crea siti web"], "c": "Assegna etichette a input dati"}
]

@app.route('/')
def home():
    weather_data = None
    city = request.args.get('city')
    if city:
        api_key = "2442065f0fdd31e1ed681c2b12a07aa4"
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={api_key}&lang=it"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = response.json()
        except Exception as e:
            print(f"Errore durante la chiamata API: {e}")
            pass
    return render_template('home.html', weather=weather_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('username')
        nick = request.form.get('nickname')
        pwd = request.form.get('password')
        confirm_pwd = request.form.get('confirm_password')

        # 1. Controllo se le password coincidono
        if pwd != confirm_pwd:
            flash('Le password non coincidono! Riprova.', 'error')
            return redirect(url_for('register'))

        # 2. Controllo se l'utente o il nickname esistono già
        exists = User.query.filter((User.username == user) | (User.nickname == nick)).first()
        if exists:
            flash('Username o Nickname già occupati! Scegline altri.', 'error')
            return redirect(url_for('register'))

        # 3. Se tutto è ok, crea l'utente
        try:
            new_user = User(username=user, password=pwd, nickname=nick)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrazione completata! Ora puoi accedere.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Si è verificato un errore nel database. Riprova.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            session['nickname'] = user.nickname
            return redirect(url_for('home'))
        else:
            flash('Credenziali errate! Riprova.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/quiz')
def quiz():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    question = random.choice(quiz_data)
    options = list(question['a'])
    random.shuffle(options)
    return render_template('quiz.html', q=question, options=options, score=user.score)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    if 'user_id' not in session: return redirect(url_for('login'))
    user_answer = request.form.get('answer')
    correct_answer = request.form.get('correct')

    if user_answer == correct_answer:
        user = User.query.get(session['user_id'])
        user.score += 10
        db.session.commit()
    return redirect(url_for('quiz'))

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.score.desc()).limit(10).all()
    return render_template('leaderboard.html', users=users)

# Inizializzazione Database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)