from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy.exc import SQLAlchemyError

#from app.routes import bp
from app import db

from app.forms import LoginForm, RegistrationForm, PatientRegistrationForm, \
    PatientVisitForm, DoctorPatientVisitForm, BillingForm
from app.models import Queue, User, Billing, Patient, PatientVisit, DoctorNotes
from flask_login import current_user, login_user, logout_user, login_required


bp = Blueprint('routes', __name__)


@bp.route('/index')
@login_required
def index():
    return render_template('index.html')


@bp.route('/', methods=["GET",'POST'])
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
        return redirect(url_for('routes.index'))
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
        return redirect(url_for('routes.view_queue'))
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
            doctor_notes=form2.doctor_notes.data,
            medications=form2.medications.data,
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
        return redirect(url_for('routes.view_queue'))
    return render_template('appointment_details.html',doctor_name=current_user.username, appointment=appointment, appointment1=appointment1,form2=form2, appointment2=appointment2)


@bp.route('/patient_visitentry', methods=['GET', 'POST'])
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
        return redirect(url_for('routes.view_queue'))  # Change to your actual redirect route

    return render_template('patient_visitentry.html', form=form)


@bp.route('/patient_details/<appointment_id>', methods=['GET', 'POST'])
def patient_details(appointment_id):
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('routes.index'))
    patient=Patient.query.filter_by(id=Patient.id).first()
    waiting_queue = Queue.query.filter(Queue.status == 'waiting')
    patientvisit = PatientVisit.query.filter_by(appointment_id=appointment_id).first()
    if patient is None:
        return "Patient not found", 404
    form2 = DoctorPatientVisitForm()
    if request.method == "POST":
        doctor = DoctorNotes(
            doctor_notes=form2.doctor_notes.data,
            medications=form2.medications.data,
            appointment_id = patientvisit.appointment_id
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
        return redirect(url_for('routes.view_queue'))
    return render_template('patient_details.html', patient=patient, patient_id=patient.id, patientvisit=patientvisit, form2=form2, waiting_queue=waiting_queue)


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

