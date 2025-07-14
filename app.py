from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, session
import os
import sqlite3
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 읽기

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_FILE = 'uploads.db'

# Wasabi 환경변수
WASABI_ACCESS_KEY_ID = os.getenv('WASABI_ACCESS_KEY_ID')
WASABI_SECRET_ACCESS_KEY = os.getenv('WASABI_SECRET_ACCESS_KEY')
WASABI_BUCKET_NAME = os.getenv('WASABI_BUCKET_NAME')
WASABI_ENDPOINT = os.getenv('WASABI_ENDPOINT')  # 예: https://s3.ap-northeast-1.wasabisys.com

# boto3 S3 클라이언트 초기화 (Wasabi 엔드포인트 지정)
s3_client = boto3.client(
    's3',
    endpoint_url=WASABI_ENDPOINT,
    aws_access_key_id=WASABI_ACCESS_KEY_ID,
    aws_secret_access_key=WASABI_SECRET_ACCESS_KEY
)

# 관리자 비밀번호
ADMIN_PASSWORD = '1234'

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

def upload_to_wasabi(local_path, wasabi_path):
    try:
        with open(local_path, 'rb') as f:
            s3_client.upload_fileobj(f, WASABI_BUCKET_NAME, wasabi_path)
    except NoCredentialsError:
        raise Exception("Wasabi credentials not available or incorrect.")
    except ClientError as e:
        raise Exception(f"Wasabi upload error: {e}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        device = request.form.get('device', '')

        file = request.files['file']
        if file.filename == '':
            flash('파일을 선택해주세요.', 'error')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # 로컬 저장

        # Wasabi 업로드 경로 예: uploads/filename.ext
        wasabi_path = f'uploads/{filename}'
        try:
            upload_to_wasabi(file_path, wasabi_path)
        except Exception as e:
            flash(f'Wasabi 업로드 실패: {e}', 'error')
            return redirect(request.url)

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
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', values)
                conn.commit()
                flash('업로드 성공!', 'success')
        except Exception as e:
            flash(f'오류 발생: {e}', 'error')
            return redirect(request.url)

        return redirect(url_for('upload_file'))

    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('비밀번호가 틀렸습니다.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('로그아웃 되었습니다.', 'success')
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('관리자 로그인 후 이용하세요.', 'error')
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
        print("❌ 관리자 페이지 오류:", e)
        return "관리자 페이지 조회 중 오류가 발생했습니다.", 500

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    # 로컬 저장된 파일을 다운로드할 때 사용 (선택사항)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete(file_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT filename FROM uploads WHERE id=?", (file_id,))
            row = c.fetchone()
            if row:
                filename = row[0]
                c.execute("DELETE FROM uploads WHERE id=?", (file_id,))
                conn.commit()
                local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(local_path):
                    os.remove(local_path)
                flash('데이터와 파일이 삭제되었습니다.', 'success')
            else:
                flash('삭제할 데이터를 찾을 수 없습니다.', 'error')
    except Exception as e:
        flash(f'삭제 중 오류 발생: {e}', 'error')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)


