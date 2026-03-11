import os
import sqlite3
import random
import re
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import urllib.request
import urllib.error
import urllib.parse  # <-- NEW: Needed to safely encode the URL


app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Database Setup
def init_db():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    # Updated: Added youtube_id and youtube_start columns
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  quiz_id INTEGER,
                  question_text TEXT, 
                  media_type TEXT, 
                  media_path TEXT, 
                  audio_path TEXT,
                  opt_a TEXT, opt_b TEXT, opt_c TEXT, opt_d TEXT,
                  correct_opt TEXT,
                  youtube_id TEXT,
                  youtube_start INTEGER,
                  FOREIGN KEY(quiz_id) REFERENCES quizzes(id))''')
    conn.commit()
    conn.close()


init_db()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_youtube_embeddable(youtube_url):
    try:
        # Safely encode the URL so special characters don't break the request
        encoded_url = urllib.parse.quote(youtube_url, safe='')
        oembed_url = f"https://www.youtube.com/oembed?url={encoded_url}&format=json"

        # Pretend to be a normal web browser (YouTube sometimes ignores Python bots)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(oembed_url, headers=headers)

        urllib.request.urlopen(req)
        return True  # It succeeded, video is embeddable

    except urllib.error.HTTPError as e:
        return False  # Throws 401 Unauthorized if embedding is disabled
    except Exception:
        return False

# --- WEB ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/creator')
def creator():
    return render_template('creator.html')


@app.route('/play/<int:quiz_id>')
def play(quiz_id):
    return render_template('player.html', quiz_id=quiz_id)


# --- API ROUTES ---
@app.route('/api/quizzes', methods=['GET', 'POST'])
def handle_quizzes():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        c.execute("INSERT INTO quizzes (name) VALUES (?)", (name,))
        quiz_id = c.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'id': quiz_id, 'name': name, 'status': 'success'})

    c.execute("SELECT * FROM quizzes")
    quizzes = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(quizzes)


@app.route('/api/questions', methods=['POST'])
def add_question():
    media_file = request.files.get('media_file')
    audio_file = request.files.get('audio_file')

    media_path, audio_path = "", ""

    if media_file and allowed_file(media_file.filename):
        filename = secure_filename(media_file.filename)
        media_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        media_path = f"{UPLOAD_FOLDER}/{filename}"

    if audio_file and allowed_file(audio_file.filename):
        filename = secure_filename(audio_file.filename)
        audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        audio_path = f"{UPLOAD_FOLDER}/{filename}"

    data = request.form
    youtube_url = data.get('youtube_url', '')
    youtube_start = data.get('youtube_start', 0)
    if not youtube_start:
        youtube_start = 0

    youtube_id = ""
    if youtube_url:
        # NEW: Check if YouTube allows embedding BEFORE saving!
        if not is_youtube_embeddable(youtube_url):
            return jsonify({'status': 'error',
                            'message': 'The creator of this YouTube video has disabled embedding. Please use a different link (like a fan-made lyric video).'}), 400

        match = re.search(r'(?:v=|\/|youtu\.be\/|embed\/)([0-9A-Za-z_-]{11})', youtube_url)
        if match:
            youtube_id = match.group(1)

    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute('''INSERT INTO questions 
                 (quiz_id, question_text, media_type, media_path, audio_path, 
                  opt_a, opt_b, opt_c, opt_d, correct_opt, youtube_id, youtube_start)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['quiz_id'], data['question_text'], data['media_type'],
               media_path, audio_path, data['opt_a'], data['opt_b'],
               data['opt_c'], data['opt_d'], data['correct_opt'], youtube_id, int(youtube_start)))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/quiz/<int:quiz_id>/questions')
def get_quiz_questions(quiz_id):
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
    rows = c.fetchall()
    conn.close()

    questions = []
    for r in rows:
        questions.append({
            'id': r[0], 'question_text': r[2], 'media_type': r[3],
            'media_path': r[4], 'audio_path': r[5],
            'opt_a': r[6], 'opt_b': r[7], 'opt_c': r[8], 'opt_d': r[9],
            'correct_opt': r[10], 'youtube_id': r[11], 'youtube_start': r[12]
        })

    random.shuffle(questions)
    return jsonify(questions[:10])


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)