from flask import Blueprint, render_template, session
from utils.auth import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    user_email = session.get('user_email')
    # Kullanıcıya özel analiz/geçmiş çekilebilir
    return render_template('index.html', user_email=user_email)