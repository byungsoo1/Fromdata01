from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, session
import os
import sqlite3
from werkzeug.utils import secure_filename
import dropbox

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_FILE = 'uploads.db'

# Dropbox 토큰 (사용자님 토큰으로 교체)
DROPBOX_ACCESS_TOKEN = 'sl.u.AF2x50wREBjtXLRP1ZmZWvaoIC6r_PglYVVYq6majDNLpaye0DnfUX5KKfgrNt1JuCq6X9bC7Cu2fUl5F1k6MZxJeVP_X2bD6FNkFkfLVKfhJ_Vb13wI4BCKC-mTzgMdZIMS9RYvHpTC2Cmlga3rQCfFCYk_FNMdmfyMNnpdst247Xl-Bvb1DnAbfDPBptT_5q9OgR-4fa5kI8eaGoDAJtp4eRdQ-fllEV1ZDn7hHk-uVy8Rvzja1NOBsVmMTIJ1TOtY9GOHwdf9h7BKX2nNHanTJKGAy0dmXWbnoN_5FgQ_Cp9W3d9-6Am-iFnoLN4O1ctls5ECJmbWvPtlL3ZZYbIokwdYslgKdGbEl16zt2SvTdGmwSzBSMA69cSRL1tj-L5r96NLn_DZK1wPJpeNmfzrA-cjkRAadsQE2p9LI6gmXl-m79CHUsxt_PA3DNSCv4nE7iWLryNcNRW87H9PUQpCs7YIv6G2uXtvVDEqEx4g2cu-o0tk4qzHHyoLPNCYUAz5Ifmhj4YQZvMMO-0m_8d5SpFvC7TPU3YHS_q1vJfpJGJ_G4bFPvNIt9FBl_nKYhfWzoPb8iSwhogTBU0gODrDLTVjcwpBl821AvHukSZZETxBVbIXMak8Nz5UFk13HDnOry6HyqQ3eIaPNN3Phbyof48RA1pq3ickqu-fMZ90bxclccg1w8hHHlGIudBfn1XRqr-Kiuyu4VqTqQCU4fRONlXrNyIe2-QQb_U4WBwb_sSaT9hvVi5tzCeEE2pOjVG-pvCLViX80k_eA4at7y9FSjthdOALXWMP4KPmA7FUXhPV93C30iPyrdQNRp2qNZ8TqL-eCCMVrWkxC6gWtxL7rw-5Z4lGGRzQKJ2XrYU12vPNTjkH7VyI8HYyN59kGw8EPJR-OhGyTVtPg2-SNCTdArkJQN6vQexKV_Tnldg6UYNuqZP2CEEZztPs8aE-vgZNU7-_Ht0Sl6vXbCWyJqMzpyFgCY9N4mgb87-F6m4S4LX3cnsrAL-DOGVEUIkpD4uHpGedE6HCWgz5dv_zBey7Y37pifkc9l9aFnJoRRioRCPJWZkLKfvGwcu8YOmIuV79OSsyZLM_UJ45Db_gJBJ5X-C4MOQxVIp7iLx7LwxtHSQrDAdK-2TtKjUC6_DuFZQDTUs2VqL6N00j3lLJCSuvZGQQ9BnvwW_NleKx0ZjlBk1sLtON0Le5zFvmL5n0BmuXazNJ845frMb6U-ZnARH_CDKyzgUYzr0RNQEAeH0UZRLF7u_avvE9aDYQvjnYyn8'

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

def upload_to_dropbox(local_path, dropbox_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(local_path, 'rb') as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

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

        # Dropbox 업로드 경로 예: /uploads/filename.ext
        dropbox_path = f'/uploads/{filename}'
        try:
            upload_to_dropbox(file_path, dropbox_path)
        except Exception as e:
            flash(f'Dropbox 업로드 실패: {e}', 'error')
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

        # 디버깅용 로그 출력
        print(f"sections 길이: {len(sections)}")  # 20개여야 함
        print(f"values 길이: {len(values)}")      # 30개여야 함

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
            # 삭제할 파일명 얻기
            c.execute("SELECT filename FROM uploads WHERE id=?", (file_id,))
            row = c.fetchone()
            if row:
                filename = row[0]
                # DB에서 삭제
                c.execute("DELETE FROM uploads WHERE id=?", (file_id,))
                conn.commit()
                # 로컬 파일 삭제
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


