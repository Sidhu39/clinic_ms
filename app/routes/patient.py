from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

from app.models import PatientPass, DoctorNotes

bp = Blueprint('patient', __name__)

@bp.route('/<patient_id>')
@login_required
def patient_dashboard(patient_id):
    patient = PatientPass.query.filter_by(patient_id=patient_id).all()
    doctor_notes = DoctorNotes.query.filter_by(patient_id=patient_id).all()
    return render_template('patient/dashboard.html', title='Patient Dashboard', doctor_notes=doctor_notes, patient=patient)
