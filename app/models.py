"""from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, login
from werkzeug import generate_password_hash, check_password_hash



@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), index=True)  # Add a role field

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    doctor = db.Column(db.String(120), nullable=False)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    queue_position = db.Column(db.Integer, nullable=True)  # Add this line

    def __repr__(self):
        return f'<Appointment {self.id} - {self.date} {self.time} with {self.doctor}>'


class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Unpaid')

    def __repr__(self):
        return f'<Billing {self.id} - Appointment {self.appointment_id} - {self.amount} - {self.status}>'
    """
import random
import string
# app/models.py

import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from flask_login import UserMixin

def generate_appointment_id(prebooked=True):
    # Generate 4 random digits
    number_part = ''.join(random.choices('0123456789', k=4))
    # Generate 1 random uppercase alphabet
    alphabet_part = random.choice(string.ascii_uppercase)

    if prebooked:
        prefix = 'G'
    else:
        prefix = 'H'

    appointment_id = f"{prefix}{number_part}{alphabet_part}"
    return appointment_id

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    appointment_id = db.Column(db.String(64), db.ForeignKey('patientvisit.appointment_id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(64), nullable=False, default='waiting')
    appointment = db.relationship('PatientVisit', backref=db.backref('queues', lazy=True))
'''class Prescription(db.Model):
    __tablename__ = 'prescription'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.String(64), db.ForeignKey('patient.id'))
    doctor_notes = db.Column(db.Text, nullable=False)
    medications = db.Column(db.Text, nullable=False)
    follow_up = db.Column(db.Boolean, default=False)
    appointment = db.relationship('Patient', backref=db.backref('prescription', lazy=True))

    def __repr__(self):
        return f"<PatientPrescibed {self.patient_name}>"'''

class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    appointment_id = db.Column(db.String(64), db.ForeignKey('patient.patient_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Unpaid')
    appointment = db.relationship('Patient', backref=db.backref('billings', lazy=True))

class PatientVisit(db.Model):
    __tablename__ = 'patientvisit'

    id = db.Column(db.Integer, primary_key=True)

    # Unique appointment ID
    appointment_id = db.Column(db.String(64), unique=True, nullable=False)
    patient = db.relationship('Patient', backref=db.backref('visits', lazy=True))

    # Patient link
    patient_id = db.Column(db.String, db.ForeignKey('patient.patient_id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)

    # Optional slot reference for pre-booked patients
    slot_id = db.Column(db.Integer, db.ForeignKey('appointment_slot.id'), nullable=True)
    time_slot = db.Column(db.String(20), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)

    # Vital signs and condition
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    blood_pressure_high = db.Column(db.Integer, nullable=True)
    blood_pressure_low = db.Column(db.Integer, nullable=True)
    temperature = db.Column(db.Integer, nullable=True)
    blood_group = db.Column(db.String(5), nullable=False)
    medical_condition = db.Column(db.String(255), nullable=True)

    # Timestamp
    visit_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())

    def __repr__(self):
        return f"<PatientVisit {self.appointment_id} - {self.patient_name}>"

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(50), nullable=False)
    patient_id = db.Column(db.String(255), default='test', nullable=False, unique=True)
    patient_blood_group = db.Column(db.String(3), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    currentdate = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    contact_number = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)

class DoctorNotes(db.Model):
    __tablename__ = 'doctordetails'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.String(64), db.ForeignKey('patientvisit.appointment_id'), nullable=False, unique=True)
    patient_id = db.Column(db.String(64), db.ForeignKey('patient.patient_id'), nullable=False)
    doctor_notes = db.Column(db.Text, nullable=False)
    doctor_name = db.Column(db.String(50), nullable=False)
    medications = db.Column(db.Text, nullable=False)
    visit_date = db.Column(db.DateTime, db.ForeignKey('patientvisit.visit_date'), nullable=False)

class PatientPass(UserMixin, db.Model):
    __tablename__ = 'patientpass'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(64), db.ForeignKey('patient.patient_id'), nullable=False, unique=True)
    patient_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), db.ForeignKey('patient.email'), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), default='patient', nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

class AppointmentSlot(db.Model):
    __tablename__ = 'appointment_slot'
    id = db.Column(db.Integer, primary_key=True)
    doctor_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    patient_id = db.Column(db.String(64), db.ForeignKey('patient.patient_id'), nullable=True)
    is_booked = db.Column(db.Boolean, default=False)