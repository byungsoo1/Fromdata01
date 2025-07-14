import os
import sqlite3
import uuid
import dropbox
from flask import Flask, request, redirect, render_template, url_for, flash

# Dropbox 토큰 및 경로 설정
DROPBOX_ACCESS_TOKEN = "sl.u.AF2x50wREBjtXLRP1ZmZWvaoIC6r_PglYVVYq6majDNLpaye0DnfUX5KKfgrNt1JuCq6X9bC7Cu2fUl5F1k6MZxJeVP_X2bD6FNkFkfLVKfhJ_Vb13wI4BCKC-mTzgMdZIMS9RYvHpTC2Cmlga3rQCfFCYk_FNMdmfyMNnpdst247Xl-Bvb1DnAbfDPBptT_5q9OgR-4fa5kI8eaGoDAJtp4eRdQ-fllEV1ZDn7hHk-uVy8Rvzja1NOBsVmMTIJ1TOtY9GOHwdf9h7BKX2nNHanTJKGAy0dmXWbnoN_5FgQ_Cp9W3d9-6Am-iFnoLN4O1ctls5ECJmbWvPtlL3ZZYbIokwdYslgKdGbEl16zt2SvTdGmwSzBSMA69cSRL1tj-L5r96NLn_DZK1wPJpeNmfzrA-cjkRAadsQE2p9LI6gmXl-m79CHUsxt_PA3DNSCv4nE7iWLryNcNRW87H9PUQpCs7YIv6G2uXtvVDEqEx4g2cu-o0tk4qzHHyoLPNCYUAz5Ifmhj4YQZvMMO-0m_8d5SpFvC7TPU3YHS_q1vJfpJGJ_G4bFPvNIt9FBl_nKYhfWzoPb8iSwhogTBU0gODrDLTVjcwpBl821AvHukSZZETxBVbIXMak8Nz5UFk13HDnOry6HyqQ3eIaPNN3Phbyof48RA1pq3ickqu-fMZ90bxclccg1w8hHHlGIudBfn1XRqr-Kiuyu4VqTqQCU4fRONlXrNyIe2-QQb_U4WBwb_sSaT9hvVi5tzCeEE2pOjVG-pvCLViX80k_eA4at7y9FSjthdOALXWMP4KPmA7FUXhPV93C30iPyrdQNRp2qNZ8TqL-eCCMVrWkxC6gWtxL7rw-5Z4lGGRzQKJ2XrYU12vPNTjkH7VyI8HYyN59kGw8EPJR-OhGyTVtPg2-SNCTdArkJQN6vQexKV_Tnldg6UYNuqZP2CEEZztPs8aE-vgZNU7-_Ht0Sl6vXbCWyJqMzpyFgCY9N4mgb87-F6m4S4LX3cnsrAL-DOGVEUIkpD4uHpGedE6HCWgz5dv_zBey7Y37pifkc9l9aFnJoRRioRCPJWZkLKfvGwcu8YOmIuV79OSsyZLM_UJ45Db_gJBJ5X-C4MOQxVIp7iLx7LwxtHSQrDAdK-2TtKjUC6_DuFZQDTUs2VqL6N00j3lLJCSuvZGQQ9BnvwW_NleKx0ZjlBk1sLtON0Le5zFvmL5n0BmuXazNJ845frMb6U-ZnARH_CDKyzgUYzr0RNQEAeH0UZRLF7u_avvE9aDYQvjnYyn8"
DROPBOX_UPLOAD_PATH = "/FromData_Result"  # 폴더명 변경됨

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
        device = request.form.get('device', '')
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
                flash("\u274c Dropbox \uc5c5\ub85c\ub4dc \uc2e4\ud328: " + str(e), "error")
                return redirect(url_for('upload_file'))

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
            ''', (name, phone, device, unique_filename, 0, *sections,
                  washer, aircon, additional_appliances_1, additional_appliances_2, residence))
            conn.commit()
            conn.close()
            flash("\u2705 \uc5c5\ub85c\ub4dc \uc644\ub8cc \ubc0f Dropbox \uc800\uc7a5 \uc131\uacf5!", "success")
            return redirect(url_for('upload_file'))

    return render_template('upload.html')


