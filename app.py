from flask import Flask, request, render_template, flash, redirect
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = './uploads.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("✅ POST 요청 도착 - 디버깅 시작")

        name = request.form.get('name', '')
        phone = request.form.get('phone', '')
        device = request.form.get('device', '')

        file = request.files.get('file')
        if not file:
            flash('파일이 선택되지 않았습니다.', 'error')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        unique_filename = filename
        file.save(os.path.join(UPLOAD_FOLDER, unique_filename))

        # sections, scenarios 합치기 (10개씩 총 20개)
        sections = []
        for i in range(1, 11):
            section_val = request.form.get(f'section_{i}', '')
            scenario_val = request.form.get(f'scenario_{i}', '')
            sections.append(section_val)
            sections.append(scenario_val)

        print(f"sections 개수: {len(sections)}")  # 20개여야 함
        print("sections 내용:", sections)

        washer = request.form.get('washer', '')
        aircon = request.form.get('aircon', '')
        additional_appliances_1 = request.form.get('additional_appliances_1', '')
        additional_appliances_2 = request.form.get('additional_appliances_2', '')
        residence = request.form.get('residence', '')

        # 총 29개 값이 맞는지 확인
        values = (
            name, phone, device, unique_filename, 0,
            *sections,
            washer, aircon, additional_appliances_1, additional_appliances_2, residence
        )

        print(f"values 개수: {len(values)}")  # 반드시 29개여야 함
        print("values 내용:", values)

        try:
            conn = get_db()
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
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?, ?, ?, ?
                )
            ''', values)
            conn.commit()
            flash('업로드 성공!', 'success')
            print("✅ DB 저장 성공")
        except Exception as e:
            print("❌ DB 저장 중 오류:", e)
            flash(f'오류 발생: {e}', 'error')
            return redirect(request.url)
        finally:
            conn.close()

        return redirect(request.url)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)


