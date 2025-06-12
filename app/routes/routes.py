import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from sqlalchemy.exc import SQLAlchemyError
from app import db

from app.forms import LoginForm, RegistrationForm, PatientRegistrationForm, \
    PatientVisitForm, DoctorPatientVisitForm, BillingForm, PatientRegisterForm, PatientLoginForm
from app.models import Queue, User, Billing, Patient, PatientVisit, DoctorNotes, PatientPass, AppointmentSlot
from flask_login import current_user, login_user, logout_user, login_required


bp = Blueprint('routes', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')



@bp.route('/login', methods=["GET",'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('routes.login'))
        login_user(user, remember=form.remember_me.data)
        if current_user.role=='nurse':
            return redirect(url_for('nurse.nurse_dashboard'))
        if current_user.role=='doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        if current_user.role=='cashier':
            return redirect(url_for('cashier.cashier_dashboard'))
        return redirect(url_for('routes.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        if current_user.role == 'nurse':
            return redirect(url_for('nurse.nurse_dashboard'))
        if current_user.role == 'cashier':
            return redirect(url_for('cashier.cashier_dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        print("User added",form.username.data)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/register_patient', methods=['GET', 'POST'])
@login_required
def register_patient():
    if current_user.role != 'nurse':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('routes.index'))
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        birthdate = form.birthdate.data
        currentdate = form.currentdate.data
        age = currentdate.year - birthdate.year - (
                (currentdate.month, currentdate.day) < (birthdate.month, birthdate.day))
        patient = Patient(
                patient_name=form.patient_name.data,
                patient_id=form.patient_id.data,
                age=age,
                patient_blood_group=form.patient_blood_group.data,
                gender=form.gender.data,
                birthdate=form.birthdate.data,
                currentdate=form.currentdate.data,
                contact_number=form.contact_number.data,
                email=form.email.data,
                address=form.address.data
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient Registered successfully!', 'success')
        return redirect(url_for('nurse.nurse_dashboard'))
    return render_template('patient_register.html', title='Patient Registration', form=form)

@bp.route('/queue', methods=['GET', 'POST'])
def view_queue():
    waiting_queue =  Queue.query.filter(Queue.status=='waiting')
    billing_queue = Queue.query.filter(Queue.status=='billing')
    return render_template('view_queue.html', waiting_queue=waiting_queue, billing_queue=billing_queue)

@bp.route('/billing/<appointment_id>',methods=['POST'])
@login_required
def billing(appointment_id):
    if current_user.role != 'cashier':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('routes.index'))
    appointment = PatientVisit.query.filter_by(appointment_id=appointment_id).first()
    doctordetails = DoctorNotes.query.filter_by(appointment_id=appointment.appointment_id).first()
    appointment1 = Patient.query.filter_by(patient_name=appointment.patient_name).first()
    queue = Queue.query.filter_by(appointment_id=appointment.appointment_id).first()
    form = BillingForm()
    if not form.validate_on_submit():
        print(form.errors)
    if form.validate_on_submit():
        billing = Billing(appointment_id=appointment.appointment_id, amount=form.amount.data, status='paid')
        db.session.add(billing)
        db.session.commit()
        appointment.status = 'completed'
        db.session.delete(appointment)
        db.session.delete(queue)
        db.session.commit()
        return redirect(url_for('cashier.cashier_dashboard'))
    return render_template('billing.html', appointment=appointment, appointment1=appointment1, doctordetails=doctordetails, form=form)

@bp.route('/select_queue/<appointment_id>', methods=['GET', 'POST'])
@login_required
def select_queue(appointment_id):
    queue = Queue.query.filter_by(position=appointment_id).first()
    appointment1 = PatientVisit.query.filter_by(id=appointment_id).first()
    if queue:
        if queue.status == 'waiting' and current_user.role == 'doctor':
            queue.status = 'completed'
        elif queue.status == 'billing' and current_user.role == 'cashier':
            queue.status = 'paid'
        db.session.delete(appointment1)
        db.session.commit()
    return redirect(url_for('routes.view_queue'))

@bp.route('/appointment/<appointment_id>', methods=['GET', 'POST'])
@login_required
def appointment_details(appointment_id):
    appointment1 = PatientVisit.query.filter_by(appointment_id=appointment_id).first()
    appointment = Queue.query.filter_by(appointment_id=appointment_id).first()
    appointment2 = Patient.query.filter_by(patient_name=appointment1.patient_name).first()
    form2 = DoctorPatientVisitForm()
    if form2.validate_on_submit(): #request.method == "POST"
        doctor = DoctorNotes(
            doctor_name=current_user.username,
            patient_id=appointment1.patient_id,
            doctor_notes=form2.doctor_notes.data,
            medications=form2.medications.data,
            visit_date=appointment1.visit_date,
            appointment_id=appointment1.appointment_id
        )
        db.session.add(doctor)
        db.session.commit()
        queue = Queue.query.filter_by(appointment_id=appointment.appointment_id).first()
        queue.status = 'completed'
        existing_billing_item = Queue.query.filter_by(
            appointment_id=queue.appointment_id,
            status='billing'
        ).first()

        # Only add to billing queue if not already present
        if not existing_billing_item:
            new_queue_item = Queue(
                appointment_id=appointment1.appointment_id,
                position=Queue.query.filter_by(status='waiting').count(),
                status='billing'
            )
            db.session.add(new_queue_item)
        db.session.delete(queue)
        db.session.commit()
        return redirect(url_for('doctor.doctor_dashboard'))
    return render_template('appointment_details.html',doctor_name=current_user.username, appointment=appointment, appointment1=appointment1,form2=form2, appointment2=appointment2)


"""@bp.route('/patient_visitentry', methods=['GET', 'POST'])
@login_required
def patient_visit_entry():
    if current_user.role != 'nurse':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('routes.index'))
    form1=PatientRegistrationForm()
    form = PatientVisitForm()
    if form.validate_on_submit():

        visit = PatientVisit(
            patient_id=form1.patient_id.data,
            patient_name=form1.patient_name.data,
            height=form.height.data,
            weight=form.weight.data,
            blood_pressure_high=form.blood_pressure_high.data,
            blood_pressure_low=form.blood_pressure_low.data,
            temperature=form.temperature.data,
            medical_condition=form.medical_condition.data
        )
        db.session.add(visit)
        db.session.commit()
        queue = Queue(appointment_id=visit.appointment_id, position=Queue.query.count() + 1)
        db.session.add(queue)
        db.session.commit()
        #flash('Appointment booked successfully!', 'success')
        return redirect(url_for('nurse.nurse_dashboard'))  # Change to your actual redirect route

    return render_template('patient_visitentry.html', form=form)"""


"""@bp.route('/patient_details/<appointment_id>', methods=['GET', 'POST'])
def patient_details(appointment_id):
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('routes.index'))
    waiting_queue = Queue.query.filter(Queue.status == 'waiting')
    patientvisit = PatientVisit.query.filter_by(appointment_id=appointment_id).first()
    patient = Patient.query.filter_by(patient_id=patientvisit.patient_id).first()
    if patient is None:
        return "Patient not found", 404
    form2 = DoctorPatientVisitForm()
    if request.method == "POST":
        doctor = DoctorNotes(
            patient_id = patientvisit.patient_id,
            doctor_notes = form2.doctor_notes.data,
            medications = form2.medications.data,
            appointment_id = patientvisit.appointment_id,
        )
        db.session.add(doctor)
        db.session.commit()
        queue = Queue.query.filter_by(appointment_id=patientvisit.appointment_id).first()
        queue.status = 'completed'
        existing_billing_item = Queue.query.filter_by(
            appointment_id=queue.appointment_id,
            status='billing'
        ).first()

        # Only add to billing queue if not already present
        if not existing_billing_item:
            new_queue_item = Queue(
                appointment_id=queue.appointment_id,
                position=Queue.query.filter_by(status='billing').count() + 1,
                status='billing'
            )
            db.session.add(new_queue_item)
        db.session.delete(queue)
        db.session.commit()
        db.session.delete(patientvisit)
        db.session.commit()
        flash('Patient visit recorded successfully!', 'success')
        return redirect(url_for('doctor.doctor_dashboard'))
    return render_template('patient_details.html', patient=patient, patient_id=patient.patient_id, patientvisit=patientvisit, form2=form2, waiting_queue=waiting_queue)
"""

from flask import Flask, jsonify, request
from app.models import Patient

@bp.route('/search_patient', methods=['GET'])
def search_patient():
    patient_id = request.args.get('patient_id')
    if patient_id:
        patient = Patient.query.filter_by(patient_id=patient_id).first()
        if patient:
            return jsonify({
                'patient_name': patient.patient_name,
                # You can return other patient fields here
            })
    return jsonify({'error': 'Patient not found'}), 404

@bp.route('/patient_register', methods=['GET', 'POST'])
def patient_register():
    form = PatientRegisterForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(patient_id=form.patient_id.data).first()
        if patient:
            new_pass = PatientPass(patient_id=patient.patient_id, email=form.email.data, role='patient', patient_name=form.patient_name.data)
            new_pass.set_password(form.password.data)
            db.session.add(new_pass)
            db.session.commit()
            flash("Registered successfully!", "success")
            return redirect(url_for('routes.patient_login'))
        else:
            flash("Invalid patient ID", "danger")
    return render_template('register_patient.html', form=form)

@bp.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    form = PatientLoginForm()
    if form.validate_on_submit():
        patient_user = PatientPass.query.filter_by(patient_id=form.patient_id.data).first()
        session['patient_id'] = patient_user.patient_id
        if patient_user is None or not patient_user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('routes.patient_login'))
        login_user(patient_user)
        return redirect(url_for('patient.patient_dashboard', patient_id=patient_user.patient_id))
    return render_template('patient_login.html', form=form)

@bp.route('/patient_logout')
def patient_logout():
    logout_user()
    return redirect(url_for('routes.patient_login'))

@bp.route('/get_patient_email')
def get_patient_email():
    patient_id = request.args.get('patient_id')
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if patient:
        return jsonify({'email': patient.email})
    else:
        return jsonify({'email': ''})

"""@bp.route('/get_slots')
def get_slots():
    doctor = request.args.get('doctor')
    date_str = request.args.get('date')
    query = AppointmentSlot.query

    if doctor:
        query = query.filter_by(doctor_name=doctor)
    if date_str:
        query = query.filter_by(date=datetime.strptime(date_str, "%Y-%m-%d").date())

    slots = query.order_by(AppointmentSlot.time_slot).all()

    return jsonify([{
        'id': slot.id,
        'doctor_name': slot.doctor_name,
        'date': slot.date.strftime('%Y-%m-%d'),
        'time_slot': slot.time_slot,
        'is_booked': slot.is_booked
    } for slot in slots])"""

@bp.route('/book_slot', methods=['POST'])
def book_slot():
    data = request.get_json()
    slot_id = data.get('slot_id')
    patient_id = session.get('patient_id')

    slot = AppointmentSlot.query.get(slot_id)
    if not slot or slot.is_booked:
        return jsonify({'message': 'Slot already booked or invalid.'})

    slot.is_booked = True
    slot.patient_id = patient_id
    db.session.commit()
    print("SESSION =", session)
    return jsonify({'message': 'Slot booked successfully!'})

@bp.route('/book_appointment/<patient_id>')
@login_required
def book_appointment(patient_id):
    doctor_names = User.query.filter_by(role='doctor').with_entities(User.username).distinct().all()
    doctor_names = [d[0] for d in doctor_names]
    return render_template('book_appointment.html', doctor_names=doctor_names, patient_id=patient_id)

from datetime import datetime, timedelta, time
from app.models import AppointmentSlot, db

@bp.route('/get_slots', methods=['GET'])
def get_slots(start_hour=9, end_hour=17, days_ahead=7):
    today = datetime.today().date()

    # Get all users with role 'doctor'
    doctors = User.query.filter_by(role='doctor').with_entities(User.username).distinct().all()
    doctor_names = [doc.username for doc in doctors]

    for day_offset in range(days_ahead):
        current_date = today + timedelta(days=day_offset)

        for doctor in doctor_names:
            current_time = time(hour=start_hour)
            while current_time < time(hour=end_hour):
                # Skip lunch hour (1 PM to 2 PM)
                if time(13, 0) <= current_time < time(14, 0):
                    current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=15)).time()
                    continue

                time_str = datetime.combine(datetime.today(), current_time).strftime('%I:%M %p')

                # Avoid duplicating existing slots
                existing = AppointmentSlot.query.filter_by(
                    doctor_name=doctor,
                    date=current_date,
                    time_slot=time_str
                ).first()

                if not existing:
                    slot = AppointmentSlot(
                        doctor_name=doctor,
                        date=current_date,
                        time_slot=time_str,
                        is_booked=False
                    )
                    db.session.add(slot)

                current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=15)).time()

    db.session.commit()
    print("Time slots generated successfully.")
    patient_id = session.get('patient_id')
    doctor = request.args.get('doctor')
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    slots = AppointmentSlot.query.filter_by(doctor_name=doctor, date=date).order_by(
        AppointmentSlot.time_slot).all()

    existing_booking = AppointmentSlot.query.filter_by(patient_id=patient_id, is_booked=True).first()
    if existing_booking:
        return jsonify({'message': 'You have already booked a slot. Multiple bookings are not allowed.'})

    return jsonify([
        {
            'id': s.id,
            'doctor_name': s.doctor_name,
            'date': s.date.strftime('%Y-%m-%d'),
            'time_slot': s.time_slot,
            'is_booked': s.is_booked
        } for s in slots
    ])

@bp.route('/create_slots')
def create_slots():
    get_slots()
    return "Slots created successfully."


"""patient_id = session.get('patient_id')

                slots = AppointmentSlot.query.filter_by(doctor_name=doctor, date=date).order_by(
                    AppointmentSlot.time_slot).all()

                existing_booking = AppointmentSlot.query.filter_by(patient_id=patient_id, is_booked=True).first()
                if existing_booking:
                    return jsonify({'message': 'You have already booked a slot. Multiple bookings are not allowed.'})

                return jsonify([
                    {
                        'id': s.id,
                        'doctor_name': s.doctor_name,
                        'date': s.date.strftime('%Y-%m-%d'),
                        'time_slot': s.time_slot,
                        'is_booked': s.is_booked
                    } for s in slots
                ])"""