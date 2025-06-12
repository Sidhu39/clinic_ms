import datetime

from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.forms import PatientVisitForm, PreVisitForm

from app.models import AppointmentSlot, Patient, PatientVisit, generate_appointment_id, Queue

bp = Blueprint('nurse', __name__)

@bp.route('/', methods=["GET",'POST'])
@bp.route('/nurse', methods=["GET",'POST'])
@login_required
def nurse_dashboard():
    if current_user.role != 'nurse':
        return redirect(url_for('routes.index'))
    return render_template('nurse/dashboard.html', title='Nurse Dashboard', nurse_name=current_user.username)

@bp.route('/nurse/prebooked')
def nurse_prebooked():
    slots = AppointmentSlot.query.filter(AppointmentSlot.is_booked == True).all()
    return render_template('nurse_prebooked.html', slots=slots)


@bp.route('/nurse/previsit/<int:slot_id>', methods=['GET', 'POST'])
def nurse_previsit(slot_id):
    slot = AppointmentSlot.query.get_or_404(slot_id)
    patient = Patient.query.filter_by(patient_id=slot.patient_id).first()
    form = PreVisitForm()
    if request.method == 'POST':
        visit = PatientVisit(
            appointment_id=generate_appointment_id(),
            patient_id=slot.patient_id,
            patient_name=patient.patient_name,
            slot_id=slot.id,
            time_slot=slot.time_slot,
            height=form.height.data,
            weight=form.weight.data,
            doctor_name=slot.doctor_name,
            blood_pressure_high=form.blood_pressure_high.data,
            blood_pressure_low=form.blood_pressure_low.data,
            temperature=form.temperature.data,
            medical_condition=form.medical_condition.data,
            blood_group=patient.patient_blood_group
        )
        db.session.add(visit)
        db.session.commit()
        queue = Queue(appointment_id=visit.appointment_id, position=Queue.query.count() + 1)
        db.session.add(queue)
        db.session.commit()
        db.session.delete(slot)  # ✅ Delete the slot after visit creation
        db.session.commit()
        flash('Visit saved successfully')
        return redirect(url_for('nurse.nurse_dashboard'))

    return render_template('previsit_entry.html', slot=slot, patient=patient, form=form)


@bp.route('/nurse/walkin', methods=['GET', 'POST'])
def nurse_walkin():
    form = PatientVisitForm()
    if request.method == 'POST':
        pid = request.form['patient_id']
        patient = Patient.query.filter_by(patient_id=pid).first()
        visit = PatientVisit(
            doctor_name='null',
            appointment_id=generate_appointment_id(prebooked=False),
            patient_id=patient.patient_id,
            patient_name=patient.patient_name,
            time_slot=datetime.datetime.now(),
            height=form.height.data,
            weight=form.weight.data,
            blood_pressure_high=form.blood_pressure_high.data,
            blood_pressure_low=form.blood_pressure_low.data,
            temperature=form.temperature.data,
            medical_condition=form.medical_condition.data,
            blood_group=patient.patient_blood_group
        )
        db.session.add(visit)
        db.session.commit()
        queue = Queue(appointment_id=visit.appointment_id, position=Queue.query.count() + 1)
        db.session.add(queue)
        db.session.commit()
        flash('Walk-in visit recorded')
        return redirect(url_for('nurse.nurse_dashboard'))

    return render_template('patient_visitentry.html',form=form)
