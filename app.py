from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, session
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_FILE = 'uploads.db'

# 관리자 비밀번호 (간단 예시)
ADMIN_PASSWORD = 'admin123'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                device TEXT,
                filename TEXT,
                downloaded INTEGER,
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

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        device = request.form.get('device', '')

        file = request.files.get('file')
        if not file or file.filename == '':
            flash('파일을 선택해주세요.', 'error')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        sections = []
        for i in range(1, 11):
            sections.append(request.form.get(f'section_{i}', ''))
            sections.append(request.form.get(f'scenario_{i}', ''))

        washer = request.form.get('washer', '')
        aircon = request.form.get('aircon', '')
        additional_appliances_1 = request.form.get('additional_appliances_1', '')
        additional_appliances_2 = request.form.get('additional_appliances_2', '')
        residence = request.form.get('residence', '')

        values = [
            name, phone, device, filename, 0,
            *sections,
            washer, aircon,
            additional_appliances_1, additional_appliances_2,
            residence
        ]

        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO uploads (
                        name, phone, device, filename, downloaded,
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
                    ) VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', values)
                conn.commit()
                flash('업로드 성공!', 'success')
        except Exception as e:
            flash(f'오류 발생: {e}', 'error')
            return redirect(request.url)

    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pw = request.form.get('password', '')
        if pw == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('비밀번호가 틀렸습니다.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('로그아웃 되었습니다.', 'success')
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('관리자 로그인 필요', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
def admin():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM uploads ORDER BY id DESC")
            uploads = c.fetchall()
        return render_template('admin.html', uploads=uploads)
    except Exception as e:
        return f"관리자 페이지 조회 중 오류가 발생했습니다: {e}", 500

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        flash(f'파일 다운로드 실패: {e}', 'error')
        return redirect(url_for('admin'))

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete(file_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            # 파일명 먼저 조회
            c.execute("SELECT filename FROM uploads WHERE id = ?", (file_id,))
            row = c.fetchone()
            if not row:
                flash('삭제할 파일이 없습니다.', 'error')
                return redirect(url_for('admin'))
            filename = row[0]

            # DB 레코드 삭제
            c.execute("DELETE FROM uploads WHERE id = ?", (file_id,))
            conn.commit()

        # 실제 파일 삭제
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        flash('삭제 완료!', 'success')
    except Exception as e:
        flash(f'삭제 중 오류 발생: {e}', 'error')

    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)

