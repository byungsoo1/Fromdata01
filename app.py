import os
import sqlite3
import uuid
import dropbox
from flask import Flask, request, redirect, render_template, url_for, send_from_directory, session, flash

# Dropbox 토큰 및 경로 설정
DROPBOX_ACCESS_TOKEN = "sl.u.AF1LseJCMYigriJGsLchbHVUdqmZvUJWp5SWhGdno-OZNmxgyXiGUE1ftwxT6QjabotClN0yUFW_b3Y85XKZ8DwR8ufambTI83Z4KJMWycftYEo8K2VDjUtEMvK9HfvHihn6uGPjCY6xG01Gl67apX9DW9u7WFl6uONTpMe1nijjOSUAXSdmPBm_UXg50LUmhONtSNmT8IBBexl3JuoM9npRtVtKylYByLSSBTFXwa3S1tQv1ut6J29bSz-65yk5s4HUn47CWSoRlkIq5h2nFRTixChHernjPAu3_I6OTadYRtOymZV7qj7qdEdKQzQNMvAEERpzIqDOVlYxyP5crtjPW5YDo_nNq1Y1co8H1_aZFDWqXWDnXXi4I1KtSdrUFSk6hbvs-ilB5hoH2znIK66yfMHCR5NJZfboCl_fueMemfip1rsN6xmpHnHKgEejFkc3WuqXEhWmD6Il26m4a1sH6D_ms11ItZ952O_ZxkTIrCLChdLoSnkoaPnYhTiT1m8oJ8JX0zaKtY8sdMb2ZA71OQlodES0wBL4HV5gOY272TRYPxVi6G5j-YnyZfRCd_knh5Yq4qHvrt5BNgNJlNcFYmK9u4Xw6pygqLh91dCT4yEyILsIBCHn81dbySWEtdq4SrvXYMCdNbmsM6md4OOl8bALlW_uPikGcbP9m-RYbt06lg1q6FFKfNwxu0jSvu1k3yTdZNmM2xK2-p8ozoPcZ4Ujs4YHYDYPgIS93rJzIICo_DPAr2TAhfBbdoZcMS2GnVIF4b4XvWY_n6WhnfNetGHGp3uMdDAo80b-gyXCz36e3VW2VQOk6Qb2znaoJL5wWrfI4Wy8FVE8jcMRsKhPXMoCfrFq0MSo1ahHcH5k0A4KAO2Jkuhw_aTQ-NfZ22uuhtnj4N3KA0stQesXvODuK5H234WVoEagAKxNqMGZ5zwbIgEmvffisc1_K6_wXchikBOhHenK6c0Sn-4dfZHyBHKY8w4xN7EXVnUACIMTazJz3J8KJGSIv9rmUa7Ui1iTTGDg5_4mCnD5uPDfy3cPp735paNmA09abNFqhv9Q54MA1B7uEKX0DCfStZfHCv3THxvKyBoS-xYGeVYWPpNcI8CtH5rd1f3465VgWeYc6g4pyDUiHPmCYIKIrxlwpxg4aOrnafeQmsztmaoOPORk-LkOyLjBOFnD8SDXRyQGzI-wtb0U1cTCad3nVnYCuBfVmayiUC6KHJk5oqtcDDCRBwlbsP8FPjVmCZnO2en5OD_S7dI2L5Aze6cjwlvpkLc"
DROPBOX_UPLOAD_PATH = "/FromData ReC"

app = Flask(__name__)
app.secret_key = 'your_secret_key'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DATABASE = os.path.join(BASE_DIR, 'database.db')
ADMIN_PASSWORD = '1234'

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
                flash("❌ Dropbox 업로드 실패: " + str(e), "error")
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, device, unique_filename, 0, *sections,
                  washer, aircon, additional_appliances_1, additional_appliances_2, residence))
            conn.commit()
            conn.close()
            flash("✅ 업로드 완료 및 Dropbox 저장 성공!", "success")
            return redirect(url_for('upload_file'))

    return render_template('upload.html')


