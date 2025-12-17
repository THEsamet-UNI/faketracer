from flask import Blueprint, render_template, session
from utils.auth import login_required
from models.database import get_contents_by_user_id

history_bp = Blueprint('history', __name__, url_prefix='/history')

@history_bp.route('/')
@login_required
def history():
    user_id = session.get('user_id')
    contents = get_contents_by_user_id(user_id)
    return render_template('history.html', contents=contents)
