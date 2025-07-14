import os
import sqlite3
import uuid
import dropbox
from flask import Flask, request, redirect, render_template, url_for, flash

# Dropbox 토큰 및 경로 설정
DROPBOX_ACCESS_TOKEN = "슬기롭게_토큰_입력하세요"
DROPBOX_UPLOAD_PATH = "/FromData_Result"

app = Flask(__name__)
app.secret_key = 'your_secret_key'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DATABASE = os.path.join(BASE_DIR, 'database.db')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, phone TEXT, device TEXT, filename TEXT, downloaded INTEGER DEFAULT 0,
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
            washer TEXT, aircon TEXT,
            additional_appliances_1 TEXT, additional_appliances_2 TEXT,
            residence TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def upload_to_dropbox(local_path, dropbox_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(local_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        device = request.form.get('device', '') or ''
        file = request.files['file']

        if file:
            ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(local_path)

            try:
                dropbox_path = f"{DROPBOX_UPLOAD_PATH}/{unique_filename}"
                upload_to_dropbox(local_path, dropbox_path)
            except Exception as e:
                flash("\u274c Dropbox 업로드 실패: " + str(e), "error")
                return redirect(url_for('upload_file'))

            sections = []
            for i in range(1, 11):
                sections.append(request.form.get(f'section_{i}', '') or '')
                sections.append(request.form.get(f'scenario_{i}', '') or '')

            # 로그 찍기 (디버깅용)
            print(f"✅ sections 길이: {len(sections)}")   # 꼭 20개여야 함
            print(f"📋 sections 내용: {sections}")

            washer = request.form.get('washer', '') or ''
            aircon = request.form.get('aircon', '') or ''
            additional_appliances_1 = request.form.get('additional_appliances_1', '') or ''
            additional_appliances_2 = request.form.get('additional_appliances_2', '') or ''
            residence = request.form.get('residence', '') or ''

            values_tuple = (
                name, phone, device, unique_filename, 0,
                *sections,
                washer, aircon, additional_appliances_1, additional_appliances_2, residence
            )

            print(f"✅ values_tuple 길이: {len(values_tuple)}")  # 꼭 29개여야 함
            print(f"📋 values_tuple 내용: {values_tuple}")

            conn = sqlite3.connect(DATABASE)
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
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', values_tuple)
            conn.commit()
            conn.close()
            flash("\u2705 업로드 완료 및 Dropbox 저장 성공!", "success")
            return redirect(url_for('upload_file'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

