from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, session
import os
import sqlite3
import dropbox
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 업로드 폴더 설정
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dropbox 설정
DROPBOX_TOKEN = 'sl.u.AF2x50wREBjtXLRP1ZmZWvaoIC6r_PglYVVYq6majDNLpaye0DnfUX5KKfgrNt1JuCq6X9bC7Cu2fUl5F1k6MZxJeVP_X2bD6FNkFkfLVKfhJ_Vb13wI4BCKC-mTzgMdZIMS9RYvHpTC2Cmlga3rQCfFCYk_FNMdmfyMNnpdst247Xl-Bvb1DnAbfDPBptT_5q9OgR-4fa5kI8eaGoDAJtp4eRdQ-fllEV1ZDn7hHk-uVy8Rvzja1NOBsVmMTIJ1TOtY9GOHwdf9h7BKX2nNHanTJKGAy0dmXWbnoN_5FgQ_Cp9W3d9-6Am-iFnoLN4O1ctls5ECJmbWvPtlL3ZZYbIokwdYslgKdGbEl16zt2SvTdGmwSzBSMA69cSRL1tj-L5r96NLn_DZK1wPJpeNmfzrA-cjkRAadsQE2p9LI6gmXl-m79CHUsxt_PA3DNSCv4nE7iWLryNcNRW87H9PUQpCs7YIv6G2uXtvVDEqEx4g2cu-o0tk4qzHHyoLPNCYUAz5Ifmhj4YQZvMMO-0m_8d5SpFvC7TPU3YHS_q1vJfpJGJ_G4bFPvNIt9FBl_nKYhfWzoPb8iSwhogTBU0gODrDLTVjcwpBl821AvHukSZZETxBVbIXMak8Nz5UFk13HDnOry6HyqQ3eIaPNN3Phbyof48RA1pq3ickqu-fMZ90bxclccg1w8hHHlGIudBfn1XRqr-Kiuyu4VqTqQCU4fRONlXrNyIe2-QQb_U4WBwb_sSaT9hvVi5tzCeEE2pOjVG-pvCLViX80k_eA4at7y9FSjthdOALXWMP4KPmA7FUXhPV93C30iPyrdQNRp2qNZ8TqL-eCCMVrWkxC6gWtxL7rw-5Z4lGGRzQKJ2XrYU12vPNTjkH7VyI8HYyN59kGw8EPJR-OhGyTVtPg2-SNCTdArkJQN6vQexKV_Tnldg6UYNuqZP2CEEZztPs8aE-vgZNU7-_Ht0Sl6vXbCWyJqMzpyFgCY9N4mgb87-F6m4S4LX3cnsrAL-DOGVEUIkpD4uHpGedE6HCWgz5dv_zBey7Y37pifkc9l9aFnJoRRioRCPJWZkLKfvGwcu8YOmIuV79OSsyZLM_UJ45Db_gJBJ5X-C4MOQxVIp7iLx7LwxtHSQrDAdK-2TtKjUC6_DuFZQDTUs2VqL6N00j3lLJCSuvZGQQ9BnvwW_NleKx0ZjlBk1sLtON0Le5zFvmL5n0BmuXazNJ845frMb6U-ZnARH_CDKyzgUYzr0RNQEAeH0UZRLF7u_avvE9aDYQvjnYyn8'
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

DB_FILE = 'uploads.db'

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
        file = request.files['file']

        if file.filename == '':
            flash('파일을 선택해주세요.', 'error')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Dropbox 업로드
        try:
            with open(file_path, 'rb') as f:
                dbx.files_upload(f.read(), f'/fromdata/{filename}', mode=dropbox.files.WriteMode.overwrite)
        except Exception as e:
            flash(f'Dropbox 업로드 실패: {e}', 'error')
            return redirect(request.url)

        # 입력 항목 처리
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
                        section1, scenario1, section2, scenario2,
                        section3, scenario3, section4, scenario4,
                        section5, scenario5, section6, scenario6,
                        section7, scenario7, section8, scenario8,
                        section9, scenario9, section10, scenario10,
                        washer, aircon, additional_appliances_1,
                        additional_appliances_2, residence
                    ) VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', values)
                conn.commit()
                flash('업로드 성공! (Dropbox 포함)', 'success')
        except Exception as e:
            flash(f'DB 저장 실패: {e}', 'error')
            return redirect(request.url)

    return render_template('upload.html')


@app.route('/admin')
def admin():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM uploads ORDER BY id DESC")
            uploads = c.fetchall()
        return render_template('admin.html', uploads=uploads)
    except Exception as e:
        print("❌ 관리자 페이지 오류:", e)
        return f"관리자 페이지 조회 중 오류: {e}", 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)

