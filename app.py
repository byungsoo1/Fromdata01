import os
import sqlite3
from flask import Flask, request, redirect, render_template, url_for, send_from_directory, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Render용 상대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DATABASE = os.path.join(BASE_DIR, 'database.db')
ADMIN_PASSWORD = '1234'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 업로드 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# DB 경로가 없으면 생성
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

# DB 초기화 함수
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            device TEXT,
            filename TEXT,
            downloaded INTEGER DEFAULT 0,
            section1 TEXT, scenario1 TEXT,
            section2 TEXT, scenario2 TEXT,
            section3 TEXT, scenario3 TEXT,
            section4 TEXT, scenario4 TEXT,
            section5 TEXT, scenario5 TEXT,
            section6 TEXT, scenario6 TEXT,
            section7 TEXT, scenario7 TEXT,
            section8 TEXT, scenario8 TEXT,
            section9 TEXT, scenario9 TEXT,
            section10 TEXT, scenario10 TEXT,
            washer TEXT,
            aircon TEXT,
            additional_appliances_1 TEXT,
            additional_appliances_2 TEXT,
            residence TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 작업자 업로드 페이지
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        device = request.form.get('device', '')
        file = request.files['file']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            sections = []
            for i in range(1, 11):
                sections.append(request.form.get(f'section_{i}', ''))
                sections.append(request.form.get(f'scenario_{i}', ''))

            washer = request.form.get('washer', '')
            aircon = request.form.get('aircon', '')
            additional_appliances_1 = request.form.get('additional_appliances_1', '')
            additional_appliances_2 = request.form.get('additional_appliances_2', '')
            residence = request.form.get('residence', '')

            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('''
                INSERT INTO uploads (
                    name, phone, device, filename,
                    section1, scenario1,
                    section2, scenario2,
                    section3, scenario3,
                    section4, scenario4,
                    section5, scenario5,
                    section6, scenario6,
                    section7, scenario7,
                    section8, scenario8,
                    section9, scenario9,
                    section10, scenario10,
                    washer, aircon,
                    additional_appliances_1, additional_appliances_2,
                    residence
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, device, filename, *sections,
                  washer, aircon,
                  additional_appliances_1, additional_appliances_2,
                  residence))
            conn.commit()
            conn.close()
            return '업로드 완료!'
    return render_template('upload.html')

# 관리자 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return '비밀번호가 틀렸습니다.'
    return render_template('login.html')

# 관리자 페이지
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM uploads")
    uploads = c.fetchall()
    conn.close()
    return render_template('admin.html', uploads=uploads)

# 파일 다운로드
@app.route('/download/<filename>')
def download_file(filename):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE uploads SET downloaded = 1 WHERE filename = ?", (filename,))
    conn.commit()
    conn.close()

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# 파일 삭제
@app.route('/delete/<int:file_id>', methods=['POST'])
def delete(file_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT filename FROM uploads WHERE id=?", (file_id,))
    row = c.fetchone()
    if row:
        filename = row[0]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        c.execute("DELETE FROM uploads WHERE id=?", (file_id,))
        conn.commit()
    conn.close()
    return redirect(url_for('admin'))

# 로그아웃
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=10000)
