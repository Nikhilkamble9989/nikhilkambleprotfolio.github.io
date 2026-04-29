from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField, TimeField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from datetime import date


class HSASignupForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(min=3, max=50)])
    department = SelectField('Department', choices=[
        ('', 'Select Department'),
        ('Administration', 'Administration'),
        ('Human Resources', 'Human Resources'),
        ('IT Department', 'IT Department'),
        ('Medical Records', 'Medical Records'),
        ('Operations', 'Operations'),
        ('Quality Assurance', 'Quality Assurance')
    ], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])


class HSALoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class PatientSignupForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Unknown', 'Unknown')
    ], validators=[Optional()])
    address = TextAreaField('Full Address', validators=[DataRequired(), Length(min=10, max=300)])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[DataRequired(), Length(min=2, max=100)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[DataRequired(), Length(min=10, max=20)])
    emergency_contact_relation = SelectField('Relation', choices=[
        ('', 'Select Relation'),
        ('Parent', 'Parent'),
        ('Spouse', 'Spouse'),
        ('Sibling', 'Sibling'),
        ('Child', 'Child'),
        ('Friend', 'Friend'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])


class PatientLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class DoctorForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    specialization = SelectField('Specialization', choices=[
        ('', 'Select Specialization'),
        ('General Medicine', 'General Medicine'),
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Endocrinology', 'Endocrinology'),
        ('Gastroenterology', 'Gastroenterology'),
        ('Neurology', 'Neurology'),
        ('Oncology', 'Oncology'),
        ('Ophthalmology', 'Ophthalmology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
        ('Psychiatry', 'Psychiatry'),
        ('Pulmonology', 'Pulmonology'),
        ('Radiology', 'Radiology'),
        ('Urology', 'Urology')
    ], validators=[DataRequired()])
    qualification = StringField('Qualification', validators=[DataRequired(), Length(min=2, max=200)])
    experience_years = IntegerField('Years of Experience', validators=[DataRequired(), NumberRange(min=0, max=60)])
    consultation_fee = FloatField('Consultation Fee', validators=[DataRequired(), NumberRange(min=0)])
    available_days = StringField('Available Days', validators=[Optional()], description='e.g., Mon, Tue, Wed')
    available_hours = StringField('Available Hours', validators=[Optional()], description='e.g., 9:00 AM - 5:00 PM')


class AppointmentForm(FlaskForm):
    doctor_id = SelectField('Select Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Appointment Date', validators=[DataRequired()])
    appointment_time = TimeField('Appointment Time', validators=[DataRequired()])
    reason_for_visit = TextAreaField('Reason for Visit', validators=[DataRequired(), Length(min=10, max=500)])
    symptoms = TextAreaField('Current Symptoms (if any)', validators=[Optional(), Length(max=500)])


class MedicalHistoryForm(FlaskForm):
    allergies = TextAreaField('Allergies', validators=[Optional(), Length(max=1000)])
    current_medications = TextAreaField('Current Medications', validators=[Optional(), Length(max=1000)])
    past_conditions = TextAreaField('Past Medical Conditions', validators=[Optional(), Length(max=1000)])
    chronic_diseases = TextAreaField('Chronic Diseases', validators=[Optional(), Length(max=1000)])
    past_surgeries = TextAreaField('Past Surgeries', validators=[Optional(), Length(max=1000)])
    family_history = TextAreaField('Family Medical History', validators=[Optional(), Length(max=1000)])
    lifestyle_notes = TextAreaField('Lifestyle Notes (Diet, Exercise, Smoking, Alcohol)', validators=[Optional(), Length(max=1000)])


class RescheduleForm(FlaskForm):
    new_date = DateField('New Date', validators=[DataRequired()])
    new_time = TimeField('New Time', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
