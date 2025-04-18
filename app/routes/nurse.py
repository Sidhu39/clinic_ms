from flask import Blueprint
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for

bp = Blueprint('nurse', __name__)

@bp.route('/', methods=["GET",'POST'])
@bp.route('/nurse', methods=["GET",'POST'])
@login_required
def nurse_dashboard():
    if current_user.role != 'nurse':
        return redirect(url_for('routes.index'))
    return render_template('nurse/dashboard.html', title='Nurse Dashboard', nurse_name=current_user.username)
