from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Queue, Appointment
from app.routes.routes import prescribe_medications as pl

bp = Blueprint('doctor', __name__)

@bp.route('/')
@bp.route('/doctor')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('routes.index'))
    queue_id = Queue.query.join(Appointment).order_by(Queue.position).all()
    waiting_queue = db.session.query(Queue).join(Appointment).filter(Queue.status == 'waiting').order_by(
        Queue.position).all()
    return render_template('doctor/dashboard.html',doctor_name=current_user.username,waiting_queue=waiting_queue, appointments=queue_id)
