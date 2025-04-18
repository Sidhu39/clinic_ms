from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Queue, PatientVisit, Patient


bp = Blueprint('doctor', __name__)

@bp.route('/')
@bp.route('/doctor')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('routes.index'))
    queue_id = Queue.query.filter(Queue.id)
    waiting_queue = Queue.query.filter(Queue.status=='waiting')
    return render_template('doctor/dashboard.html',doctor_name=current_user.username,waiting_queue=waiting_queue, appointments=queue_id)
