from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from mysql.connector import connect

from werkzeug.utils import secure_filename
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Настройки базы данных
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'shelterdb',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/img/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Функция для подключения к базе данных
def connect_db():
    db_host = os.environ.get('DB_HOST')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME')

    conn = connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/animals')
def get_animals():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM Animals')
    data = cursor.fetchall()

    conn.close()

    return jsonify(data)

@app.route('/delete_animal/<int:animal_id>', methods=['POST'])
def delete_animal(animal_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Выполните запрос на удаление записи
    cursor.execute('DELETE FROM Animals WHERE Animal_ID = %s', (animal_id,))
    conn.commit()

    conn.close()

    return redirect(url_for('index'))

@app.route('/add_animal', methods=['GET', 'POST'])
def add_animal():
    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor()

        name = request.form['name']
        shelter_id = 1  # Фиксированное значение Shelter_ID
        animal_type_id = 1
        gender = request.form['gender']
        age = request.form['age']
        color = request.form['color']
        breed = request.form['breed']
        features = request.form['features']
        how_found = request.form['how_found']

        # Обработка загрузки файла
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_url = filename
            else:
                # Обработка неправильного формата файла или других ошибок
                return "Error: Invalid file format or other file-related issue"
        else:
            # Если файл не был отправлен
            photo_url = None

        # Измененный запрос на добавление
        cursor.execute('''
                INSERT INTO Animals
                (Shelter_ID, Animal_Type_ID, Name, Photo, Gender, Age, Color, Breed, Features, How_Found)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (shelter_id, animal_type_id, name, photo_url, gender, age, color, breed, features, how_found))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_animal.html')



if __name__ == '__main__':
    app.run(debug=True)