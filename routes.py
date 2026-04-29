from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date
from app import app, db, login_manager
from models import HSA, Patient, Doctor, Appointment, MedicalHistory
from forms import (HSASignupForm, HSALoginForm, PatientSignupForm, PatientLoginForm,
                   DoctorForm, AppointmentForm, MedicalHistoryForm, RescheduleForm)


@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('hsa_'):
        return HSA.query.get(int(user_id.split('_')[1]))
    elif user_id.startswith('patient_'):
        return Patient.query.get(int(user_id.split('_')[1]))
    return None


def is_hsa():
    return current_user.is_authenticated and isinstance(current_user, HSA)


def is_patient():
    return current_user.is_authenticated and isinstance(current_user, Patient)


@app.route('/')
def home():
    if current_user.is_authenticated:
        if is_hsa():
            return redirect(url_for('hsa_dashboard'))
        elif is_patient():
            return redirect(url_for('patient_dashboard'))
    return render_template('home.html')


@app.route('/hsa/signup', methods=['GET', 'POST'])
def hsa_signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = HSASignupForm()
    if form.validate_on_submit():
        existing_email = HSA.query.filter_by(email=form.email.data).first()
        existing_emp_id = HSA.query.filter_by(employee_id=form.employee_id.data).first()
        
        if existing_email:
            flash('Email already registered.', 'danger')
            return render_template('hsa/signup.html', form=form)
        
        if existing_emp_id:
            flash('Employee ID already exists.', 'danger')
            return render_template('hsa/signup.html', form=form)
        
        hsa = HSA(
            full_name=form.full_name.data,
            email=form.email.data,
            employee_id=form.employee_id.data,
            department=form.department.data,
            phone=form.phone.data,
            address=form.address.data
        )
        hsa.set_password(form.password.data)
        
        db.session.add(hsa)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('hsa_login'))
    
    return render_template('hsa/signup.html', form=form)


@app.route('/hsa/login', methods=['GET', 'POST'])
def hsa_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = HSALoginForm()
    if form.validate_on_submit():
        hsa = HSA.query.filter_by(email=form.email.data).first()
        
        if hsa and hsa.check_password(form.password.data):
            login_user(hsa)
            flash('Login successful!', 'success')
            return redirect(url_for('hsa_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('hsa/login.html', form=form)


@app.route('/patient/signup', methods=['GET', 'POST'])
def patient_signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = PatientSignupForm()
    if form.validate_on_submit():
        existing_email = Patient.query.filter_by(email=form.email.data).first()
        
        if existing_email:
            flash('Email already registered.', 'danger')
            return render_template('patient/signup.html', form=form)
        
        patient = Patient(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            blood_group=form.blood_group.data,
            address=form.address.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            emergency_contact_relation=form.emergency_contact_relation.data
        )
        patient.set_password(form.password.data)
        
        db.session.add(patient)
        db.session.commit()
        
        medical_history = MedicalHistory(patient_id=patient.id)
        db.session.add(medical_history)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('patient_login'))
    
    return render_template('patient/signup.html', form=form)


@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = PatientLoginForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(email=form.email.data).first()
        
        if patient and patient.check_password(form.password.data):
            login_user(patient)
            flash('Login successful!', 'success')
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('patient/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/hsa/dashboard')
@login_required
def hsa_dashboard():
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='pending').count()
    approved_appointments = Appointment.query.filter_by(status='approved').count()
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    
    return render_template('hsa/dashboard.html',
                           total_appointments=total_appointments,
                           pending_appointments=pending_appointments,
                           approved_appointments=approved_appointments,
                           total_patients=total_patients,
                           total_doctors=total_doctors,
                           recent_appointments=recent_appointments)


@app.route('/hsa/appointments')
@login_required
def hsa_appointments():
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    else:
        appointments = Appointment.query.filter_by(status=status_filter).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('hsa/appointments.html', appointments=appointments, status_filter=status_filter)


@app.route('/hsa/appointment/<int:appointment_id>/approve', methods=['POST'])
@login_required
def approve_appointment(appointment_id):
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'approved'
    db.session.commit()
    flash('Appointment approved successfully.', 'success')
    return redirect(url_for('hsa_appointments'))


@app.route('/hsa/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled.', 'warning')
    return redirect(url_for('hsa_appointments'))


@app.route('/hsa/appointment/<int:appointment_id>/reschedule', methods=['GET', 'POST'])
@login_required
def reschedule_appointment(appointment_id):
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    form = RescheduleForm()
    
    if form.validate_on_submit():
        appointment.rescheduled_date = form.new_date.data
        appointment.rescheduled_time = form.new_time.data
        appointment.notes = form.notes.data
        appointment.status = 'rescheduled'
        db.session.commit()
        flash('Appointment rescheduled successfully.', 'success')
        return redirect(url_for('hsa_appointments'))
    
    return render_template('hsa/reschedule.html', form=form, appointment=appointment)


@app.route('/hsa/patients')
@login_required
def hsa_patients():
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    search_query = request.args.get('search', '')
    
    if search_query:
        patients = Patient.query.filter(
            (Patient.full_name.ilike(f'%{search_query}%')) |
            (Patient.email.ilike(f'%{search_query}%')) |
            (Patient.phone.ilike(f'%{search_query}%'))
        ).all()
    else:
        patients = Patient.query.order_by(Patient.created_at.desc()).all()
    
    return render_template('hsa/patients.html', patients=patients, search_query=search_query)


@app.route('/hsa/patient/<int:patient_id>')
@login_required
def hsa_patient_detail(patient_id):
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('hsa/patient_detail.html', patient=patient, appointments=appointments)


@app.route('/hsa/doctors')
@login_required
def hsa_doctors():
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    doctors = Doctor.query.order_by(Doctor.created_at.desc()).all()
    return render_template('hsa/doctors.html', doctors=doctors)


@app.route('/hsa/doctor/add', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    form = DoctorForm()
    
    if form.validate_on_submit():
        existing_email = Doctor.query.filter_by(email=form.email.data).first()
        
        if existing_email:
            flash('Email already registered.', 'danger')
            return render_template('hsa/doctor_form.html', form=form, title='Add Doctor')
        
        doctor = Doctor(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            specialization=form.specialization.data,
            qualification=form.qualification.data,
            experience_years=form.experience_years.data,
            consultation_fee=form.consultation_fee.data,
            available_days=form.available_days.data,
            available_hours=form.available_hours.data
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        flash('Doctor added successfully.', 'success')
        return redirect(url_for('hsa_doctors'))
    
    return render_template('hsa/doctor_form.html', form=form, title='Add Doctor')


@app.route('/hsa/doctor/<int:doctor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    form = DoctorForm(obj=doctor)
    
    if form.validate_on_submit():
        existing_email = Doctor.query.filter(Doctor.email == form.email.data, Doctor.id != doctor_id).first()
        
        if existing_email:
            flash('Email already registered.', 'danger')
            return render_template('hsa/doctor_form.html', form=form, title='Edit Doctor', doctor=doctor)
        
        doctor.full_name = form.full_name.data
        doctor.email = form.email.data
        doctor.phone = form.phone.data
        doctor.specialization = form.specialization.data
        doctor.qualification = form.qualification.data
        doctor.experience_years = form.experience_years.data
        doctor.consultation_fee = form.consultation_fee.data
        doctor.available_days = form.available_days.data
        doctor.available_hours = form.available_hours.data
        
        db.session.commit()
        flash('Doctor updated successfully.', 'success')
        return redirect(url_for('hsa_doctors'))
    
    return render_template('hsa/doctor_form.html', form=form, title='Edit Doctor', doctor=doctor)


@app.route('/hsa/doctor/<int:doctor_id>/toggle', methods=['POST'])
@login_required
def toggle_doctor(doctor_id):
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_active = not doctor.is_active
    db.session.commit()
    
    status = 'activated' if doctor.is_active else 'deactivated'
    flash(f'Doctor {status} successfully.', 'success')
    return redirect(url_for('hsa_doctors'))


@app.route('/hsa/reports')
@login_required
def hsa_reports():
    if not is_hsa():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    total_appointments = Appointment.query.count()
    pending_count = Appointment.query.filter_by(status='pending').count()
    approved_count = Appointment.query.filter_by(status='approved').count()
    cancelled_count = Appointment.query.filter_by(status='cancelled').count()
    rescheduled_count = Appointment.query.filter_by(status='rescheduled').count()
    completed_count = Appointment.query.filter_by(status='completed').count()
    
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    active_doctors = Doctor.query.filter_by(is_active=True).count()
    
    today = date.today()
    today_appointments = Appointment.query.filter_by(appointment_date=today).count()
    
    specialization_stats = db.session.query(
        Doctor.specialization, db.func.count(Appointment.id)
    ).join(Appointment, Doctor.id == Appointment.doctor_id).group_by(Doctor.specialization).all()
    
    return render_template('hsa/reports.html',
                           total_appointments=total_appointments,
                           pending_count=pending_count,
                           approved_count=approved_count,
                           cancelled_count=cancelled_count,
                           rescheduled_count=rescheduled_count,
                           completed_count=completed_count,
                           total_patients=total_patients,
                           total_doctors=total_doctors,
                           active_doctors=active_doctors,
                           today_appointments=today_appointments,
                           specialization_stats=specialization_stats)


@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if not is_patient():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == current_user.id,
        Appointment.appointment_date >= date.today(),
        Appointment.status.in_(['pending', 'approved', 'rescheduled'])
    ).order_by(Appointment.appointment_date).limit(3).all()
    
    total_appointments = Appointment.query.filter_by(patient_id=current_user.id).count()
    
    return render_template('patient/dashboard.html',
                           upcoming_appointments=upcoming_appointments,
                           total_appointments=total_appointments)


@app.route('/patient/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if not is_patient():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    form = AppointmentForm()
    doctors = Doctor.query.filter_by(is_active=True).all()
    form.doctor_id.choices = [(0, 'Select Doctor')] + [(d.id, f'Dr. {d.full_name} - {d.specialization}') for d in doctors]
    
    if form.validate_on_submit():
        if form.doctor_id.data == 0:
            flash('Please select a doctor.', 'danger')
            return render_template('patient/book_appointment.html', form=form, doctors=doctors)
        
        if form.appointment_date.data < date.today():
            flash('Appointment date cannot be in the past.', 'danger')
            return render_template('patient/book_appointment.html', form=form, doctors=doctors)
        
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=form.doctor_id.data,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
            reason_for_visit=form.reason_for_visit.data,
            symptoms=form.symptoms.data,
            status='pending'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment booked successfully! Awaiting approval.', 'success')
        return redirect(url_for('patient_appointments'))
    
    return render_template('patient/book_appointment.html', form=form, doctors=doctors)


@app.route('/patient/medical-history', methods=['GET', 'POST'])
@login_required
def patient_medical_history():
    if not is_patient():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    medical_history = MedicalHistory.query.filter_by(patient_id=current_user.id).first()
    
    if not medical_history:
        medical_history = MedicalHistory(patient_id=current_user.id)
        db.session.add(medical_history)
        db.session.commit()
    
    form = MedicalHistoryForm(obj=medical_history)
    
    if form.validate_on_submit():
        medical_history.allergies = form.allergies.data
        medical_history.current_medications = form.current_medications.data
        medical_history.past_conditions = form.past_conditions.data
        medical_history.chronic_diseases = form.chronic_diseases.data
        medical_history.past_surgeries = form.past_surgeries.data
        medical_history.family_history = form.family_history.data
        medical_history.lifestyle_notes = form.lifestyle_notes.data
        
        db.session.commit()
        flash('Medical history updated successfully.', 'success')
        return redirect(url_for('patient_medical_history'))
    
    return render_template('patient/medical_history.html', form=form, medical_history=medical_history)


@app.route('/patient/appointments')
@login_required
def patient_appointments():
    if not is_patient():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    upcoming = Appointment.query.filter(
        Appointment.patient_id == current_user.id,
        Appointment.appointment_date >= date.today()
    ).order_by(Appointment.appointment_date).all()
    
    past = Appointment.query.filter(
        Appointment.patient_id == current_user.id,
        Appointment.appointment_date < date.today()
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('patient/appointments.html', upcoming=upcoming, past=past)


@app.route('/patient/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def patient_cancel_appointment(appointment_id):
    if not is_patient():
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=current_user.id).first_or_404()
    
    if appointment.status in ['pending', 'approved']:
        appointment.status = 'cancelled'
        db.session.commit()
        flash('Appointment cancelled successfully.', 'warning')
    else:
        flash('Cannot cancel this appointment.', 'danger')
    
    return redirect(url_for('patient_appointments'))
