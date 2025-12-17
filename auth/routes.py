from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Bu e-posta ile zaten kayıt olunmuş.', 'danger')
            return redirect(url_for('auth.register'))
        user = User.create(email, password)
        if user:
            flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        flash('Kayıt sırasında bir hata oluştu.', 'danger')
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get_by_email(email)
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('index'))
        flash('Giriş başarısız! Bilgilerden emin olun.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('auth.login'))