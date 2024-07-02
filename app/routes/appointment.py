from flask import Blueprint, render_template, flash, redirect, url_for
from app import db
from app.forms import AppointmentForm
from app.models import User, Appointment
from flask_login import current_user, login_required

bp = Blueprint('appointment', __name__)

@bp.route('/')
@bp.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    form = AppointmentForm()
    if form.validate_on_submit():
        appointment = Appointment(
            patient_id=form.patient_id.data,
            date=form.date.data,
            time=form.time.data,
            doctor_id=form.doctor_id.data,
            doctor_name=form.doctor.data,
            reason=form.reason.data,
            patient_name=form.patient_name.data,
            patient_weight=form.patient_weight.data,
            patient_blood_group=form.patient_blood_group.data,
            patient_height=form.patient_height.data,
            status='waiting'  # Default status
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('appointment.html', form=form)
