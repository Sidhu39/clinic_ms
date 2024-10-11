from datetime import datetime
import random
import string
from pydoc import classname

from alembic.ddl.base import format_column_name
from wtforms.validators import Optional
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField
from wtforms import DateField,TimeField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class PatientRegistrationForm(FlaskForm):

    patient_name = StringField('Patient Name', validators=[DataRequired(), Length(min=2, max=50)])
    patient_id = StringField('Patient ID', validators=[DataRequired(), Length(min=1, max=10)])
    patient_blood_group = SelectField('Blood Group',
                                      choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'),
                                               ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')],
                                      validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                         validators=[DataRequired()])
    birthdate = DateField('Birthdate', format='%Y-%m-%d', validators=[DataRequired()])
    currentdate = DateField('Current Date', format='%Y-%m-%d', default=datetime.today, validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    def calculate_age(self):
        birthdate = self.birthdate.data
        currentdate = self.currentdate.data
        age = currentdate.year - birthdate.year - (
                (currentdate.month, currentdate.day) < (birthdate.month, birthdate.day))
        return age

    age = IntegerField('Age', render_kw={'readonly': True})
    submit = SubmitField('Register')
    '''default = currentdate.default.year - birthdate.default.year - (
            (currentdate.default.month, currentdate.default.day) < (birthdate.default.month, birthdate.default.day))'''

    '''def validate_age_field(self):
        self.age.data = self.calculate_age()
        return True'''

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('doctor', 'Doctor'), ('nurse', 'Nurse'), ('cashier', 'Cashier')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
class QueueForm(FlaskForm):
    queue_position = IntegerField('Queue Position', validators=[DataRequired()])
    submit = SubmitField('Update Queue Position')

'''class PrescriptionForm(FlaskForm):
    doctor_notes = TextAreaField('Doctor\'s Notes', validators=[DataRequired()])
    appointment_id = SelectField('Appointment', coerce=int)
    medications = TextAreaField('Medications', validators=[DataRequired()])
    follow_up = BooleanField('Follow-up Required')
    submit = SubmitField('Submit Prescription')'''

class BillingForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    submit = SubmitField('Generate Bill')
    billing_queue = SelectField('Billing Queue', choices=[], coerce=int)


class PatientVisitForm(FlaskForm):

    patient_id = StringField('Patient ID', validators=[DataRequired(), Length(min=1, max=20)])
    patient_name = StringField('Patient Name', validators=[DataRequired(), Length(min=1, max=100)])
    height = FloatField('Height (cms)', validators=[DataRequired()])
    weight = FloatField('Weight (kgs)', validators=[DataRequired()])
    age = IntegerField('Age', render_kw={'readonly': True})
    blood_pressure_high = FloatField('Blood Pressure High', validators=[DataRequired()])
    blood_pressure_low = FloatField('Blood Pressure Low', validators=[DataRequired()])
    temperature = FloatField('Temperature (F)', validators=[DataRequired()])
    medical_condition = StringField('Medical Condition', validators=[DataRequired(), Length(min=1, max=255)])
    reason = StringField('Reason for Appointment')
    medications = TextAreaField('Medications', validators=[DataRequired()])
    doctor_notes = TextAreaField('Doctor\'s Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')

