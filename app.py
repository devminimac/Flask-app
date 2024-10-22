from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)

# กำหนดโฟลเดอร์ที่จะใช้เก็บไฟล์ที่อัปโหลด
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

# ตรวจสอบให้แน่ใจว่าโฟลเดอร์ uploads มีอยู่
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ตั้งค่า secret key
app.secret_key = 'your_generated_secret_key'

# ตั้งค่า login manager
login_manager = LoginManager()
login_manager.init_app(app)

# ตัวอย่างผู้ใช้
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# ผู้ใช้ที่อนุญาตให้เข้าสู่ระบบ
users = {'admin': '1234'}  # เปลี่ยนเป็นชื่อผู้ใช้และรหัสผ่านที่ต้องการ

# ฟังก์ชันเพิ่มผู้ใช้
def add_user(username, password):
    if username in users:
        return f"ผู้ใช้ {username} มีอยู่แล้ว"
    else:
        users[username] = password
        return f"เพิ่มผู้ใช้ {username} สำเร็จ"
    
# ทดสอบเพิ่มผู้ใช้
print(add_user('teacher', '1234'))  # เพิ่มผู้ใช้ใหม่
print(add_user('admin', '1234'))         # ทดสอบเพิ่มผู้ใช้ที่มีอยู่แล้ว

@app.route('/add_user', methods=['GET', 'POST'])
def add_user_route():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # เรียกฟังก์ชันเพื่อเพิ่มผู้ใช้
        result = add_user(username, password)  
        flash(result)  # แสดงผลลัพธ์การเพิ่มผู้ใช้
        return redirect(url_for('user_management'))  # กลับไปที่หน้า User Management

    return render_template('user_management.html')  # ส่งกลับฟอร์มในกรณี GET

# Route สำหรับหน้า User Management
@app.route('/user_management', methods=['GET'])
@login_required
def user_management():
    return render_template('user_management.html')

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ตรวจสอบชื่อผู้ใช้และรหัสผ่าน
        if username in users and users[username] == password:
            user = User(username)
            login_user(user)
            flash('เข้าสู่ระบบสำเร็จ!', 'success')
            return redirect(url_for('index'))  # เปลี่ยนเส้นทางไปยังหน้าอื่นหลังเข้าสู่ระบบ
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')

    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ออกจากระบบเรียบร้อยแล้ว', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    student_id = request.form['student_id']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{student_id}.pdf")

    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{student_id}.pdf")
    else:
        flash('ไม่พบผลการเรียนของนักเรียนที่ระบุ', 'danger')
        return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        student_id = request.form['student_id']
        pdf_file = request.files['pdf_file']

        if pdf_file.filename != '':
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{student_id}.pdf"))
            flash('อัพโหลดไฟล์สำเร็จ!', 'success')
        else:
            flash('กรุณาเลือกไฟล์ PDF', 'danger')

    return render_template('upload.html')

# โค้ดอื่นๆ (เช่น search, upload) ที่คุณมีอยู่แล้ว

if __name__ == '__main__':
    app.run(debug=True)
