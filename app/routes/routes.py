from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy.exc import SQLAlchemyError

#from app.routes import bp
from app import db
'''from app.forms import LoginForm, RegistrationForm, PrescriptionForm, PatientRegistrationForm, \
    PatientVisitForm'''
from app.forms import LoginForm, RegistrationForm, PatientRegistrationForm, \
    PatientVisitForm
'''from app.models import Queue, Prescription, User, Billing, Patient, PatientVisit'''
from app.models import Queue, User, Billing, Patient, PatientVisit
from flask_login import current_user, login_user, logout_user, login_required


bp = Blueprint('routes', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/login', methods=['GET', 'POST'])
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
        return redirect(url_for('routes.index'))
    return render_template('login.html', title='Sign In', form=form)
    pass

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

#@bp.route('/register', methods=['GET', 'POST'])
#def register():
#    if current_user.is_authenticated:
#        return redirect(url_for('routes.index'))
#    form = RegistrationForm()
#    if form.validate_on_submit():
#        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
#        user.set_password(form.password.data)
#        db.session.add(user)
#        db.session.commit()
#        flash('Congratulations, you are now a registered user!')
#        return redirect(url_for('routes.login'))
#    return render_template('register.html', title='Register', form=form)


@bp.route('/register', methods=['GET', 'POST'])
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
    if form.is_submitted():
        patient = Patient(
                patient_name=form.patient_name.data,
                patient_id=form.patient_id.data,
                age=form.age.data,
                patient_blood_group=form.patient_blood_group.data,
                gender=form.gender.data,
                birthdate=form.birthdate.data,
                currentdate=form.currentdate.data,
                contact_number=form.contact_number.data,
                email=form.email.data
        )
        db.session.add(patient)
        db.session.commit()
        return redirect(url_for('routes.index'))
    return render_template('patient_register.html', title='Patient Registration', form=form)

@bp.route('/queue', methods=['GET', 'POST'])
@login_required
def view_queue():
    waiting_queue =  Queue.query.filter(Queue.status=='waiting')

    '''db.session.query(Queue).join(Patient).filter(Queue.status == 'waiting').order_by(
        Queue.position).all()'''
    print('test')
    billing_queue = Queue.query.filter(Queue.status=='billing')

    '''db.session.query(Queue).join(Patient).filter(Queue.status == 'billing').order_by(
        Queue.position).all()'''
    print("hello")
    return render_template('view_queue.html', waiting_queue=waiting_queue, billing_queue=billing_queue)

'''@bp.route('/prescription/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def prescribe_medications(patient_id):
    if current_user.role != 'doctor':
        return redirect(url_for('routes.index'))
    appointment = Patient.query.get_or_404(patient_id)
    form = PrescriptionForm()

    # Populate the appointment_id field with patients
    form.appointment_id.choices = [(patient.id, patient.patient_name) for patient in Patient.query.all()]

    if form.validate_on_submit():
        # Create a new Prescription object with form data
        prescription = Prescription(
            doctor_notes=form.doctor_notes.data,
            medications=form.medications.data,
            follow_up=form.follow_up.data,
            appointment_id=form.appointment_id.data
        )

        # Add and commit to the database
        try:
            db.session.add(prescription)
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback if there's an error
            print(f"Error committing to the database: {e}")
        return redirect(url_for('prescription_list'))
    return render_template('prescribe_medications.html', title='Prescribe Medications', form=form, appointment=appointment)
'''
@bp.route('/billing/<int:patient_id>',methods=['GET', 'POST'])
@login_required
def billing(patient_id):
    if current_user.role != 'cashier':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('routes.index'))
    appointment = PatientVisit.query.filter_by(id=patient_id).first()
    appointment1 = Patient.query.filter_by(id=patient_id).first()
    queue = Queue.query.filter_by(appointment_id=appointment.appointment_id).first()
    if request.method == 'POST':
        amount = request.form['amount']
        billing = Billing(appointment_id=appointment.appointment_id, amount=amount, status='paid')
        appointment.status = 'completed'
        db.session.add(billing)
        db.session.commit()
        db.session.delete(appointment)
        db.session.delete(queue)
        db.session.commit()
        return redirect(url_for('routes.view_queue'))
    return render_template('billing.html', appointment=appointment, appointment1=appointment1)

@bp.route('/select_queue/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def select_queue(patient_id):
    queue = PatientVisit.query.get_or_404(patient_id)
    if queue:
        if queue.status == 'waiting' and current_user.role == 'doctor':
            queue.status = 'completed'
        elif queue.status == 'billing' and current_user.role == 'cashier':
            queue.status = 'paid'
        db.session.commit()
    return redirect(url_for('routes.view_queue'))

@bp.route('/appointment/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def appointment_details(patient_id):
    appointment = Queue.query.get_or_404(patient_id)
    appointment1 = PatientVisit.query.filter_by(id=patient_id).first()
    appointment2 = Patient.query.filter_by(id=patient_id).first()
    if request.method == 'POST':

        queue = Queue.query.filter_by(appointment_id=appointment.appointment_id).first()
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
        return redirect(url_for('routes.view_queue'))
    return render_template('appointment_details.html',doctor_name=current_user.username, appointment=appointment, appointment1=appointment1, appointment2=appointment2)


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
            medical_condition=form.medical_condition.data,
            doctor_notes=form.doctor_notes.data,
            medications=form.medications.data
        )
        db.session.add(visit)
        db.session.commit()
        queue = Queue(appointment_id=visit.appointment_id, position=Queue.query.count() + 1)
        db.session.add(queue)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('routes.view_queue'))  # Change to your actual redirect route

    return render_template('patient_visitentry.html', form=form)


@bp.route('/patient_details/<int:patient_id>', methods=['GET', 'POST'])
def patient_details(patient_id):
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('routes.index'))
    patient=Patient.query.filter_by(id=patient_id).first()
    patientvisit=PatientVisit.query.filter_by(id=patient_id).first()
    print(patient)
    if patient is None:
        return "Patient not found", 404
    form1 = PatientRegistrationForm()
    form = PatientVisitForm()
    if form.validate_on_submit():
        visit = PatientVisit(
            patient_id=form1.patient_id.data,
            patient_name=form.patient_name.data,
            height=form.height.data,
            weight=form.weight.data,
            age=form.age.data,
            blood_pressure_high=form.blood_pressure_high.data,
            blood_pressure_low=form.blood_pressure_low.data,
            temperature=form.temperature.data,
            medical_condition=form.medical_condition.data,
        )
        db.session.add(visit)
        db.session.commit()
        db.session.delete(patient)
        db.session.delete(patientvisit)
        db.session.commit()
        flash('Patient visit recorded successfully!', 'success')
        return redirect(url_for('routes.view_queue'))
    return render_template('patient_details.html', patient=patient, patient_id=patient.id, patientvisit=patientvisit, form=form)


from flask import Flask, jsonify, request
from app.models import Patient

@bp.route('/search_patient', methods=['GET'])
def search_patient():
    patient_id = request.args.get('patient_id')
    if patient_id:
        patient = Patient.query.get_or_404(patient_id)
        if patient:
            return jsonify({
                'patient_name': patient.patient_name,
                # You can return other patient fields here
            })
    return jsonify({'error': 'Patient not found'}), 404

