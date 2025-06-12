from flask import Blueprint, render_template, redirect, url_for,session
from flask_login import login_required

from app.models import PatientPass, DoctorNotes, AppointmentSlot

bp = Blueprint('patient', __name__)

@bp.route('/<patient_id>')
@login_required
def patient_dashboard(patient_id):
    patient = PatientPass.query.filter_by(patient_id=patient_id).all()
    doctor_notes = DoctorNotes.query.filter_by(patient_id=patient_id).all()
    patient_id = session.get('patient_id')
    booked_slot = AppointmentSlot.query.filter_by(patient_id=patient_id, is_booked=True).first()
    return render_template('patient/dashboard.html', title='Patient Dashboard', doctor_notes=doctor_notes, patient=patient, booked_slot=booked_slot)
