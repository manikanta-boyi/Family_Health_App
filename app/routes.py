from flask import Blueprint,render_template, flash, redirect, url_for,request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required, current_user, logout_user
import random
from flask_mail import Message
from datetime import datetime, timedelta

from .forms import RegisterForm, LoginForm, FamilyMemberForm, HealthRecordForm, OTPForm
from app.extensions import db,login_manager,mail


from .models import User, FamilyMember, HealthRecord

main = Blueprint('main',__name__)




@main.route('/')
def home():
    return render_template('home.html')

# Generating OTP
def generate_otp():
    rand_int = random.randint(100000,999999)
    otp = str(rand_int)
    return otp

# Function for Send otp to user mail
def send_otp_mail(user_mail,otp):
    msg = Message('Your OTP for Registration', recipients=[user_mail])
    msg.body = f'Your One-Time Password (OTP) for registration is: {otp}\n\nThis OTP is valid for 10 minutes.'
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}") # For debugging
        return False


@main.route('/register',methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            if not existing_user.is_email_verified:
                # If user exists but not verified, resend OTP
                otp = generate_otp()
                existing_user.otp = otp
                existing_user.otp_generated_at = datetime.utcnow()
                db.session.commit()
                send_otp_mail(existing_user.email, otp)
                flash('An account with this email already exists but is not verified. A new OTP has been sent to your email.', 'info')
                return redirect(url_for('main.verify_otp', user_id=existing_user.id))
            else:
                flash('An account with this email already exists and is verified. Please log in.', 'warning')
                return redirect(url_for('main.login'))
            
        hashed_pw = generate_password_hash(form.password.data)
        otp = generate_otp()
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw,
                    is_email_verified=False, # Set to False initially
                    otp=otp,
                    otp_generated_at=datetime.utcnow())
        db.session.add(user)
        db.session.commit()

        if send_otp_mail(user.email,otp):
            flash('Account created successfully! A verification OTP has been sent to your email. Please verify your email.', 'success')
            return redirect(url_for('main.verify_otp', user_id=user.id))
        else:
            flash('Failed to send verification email. Please try again.', 'danger')
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('main.register'))
    return render_template('register.html',form=form)

@main.route('/verify_otp/<int:user_id>',methods=['GET','POST'])
def verify_otp(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_email_verified:
        flash('Your email is already verified. Please log in.', 'info')
        return redirect(url_for('main.login'))
    form = OTPForm()
    if form.validate_on_submit():
        # Check if OTP is expired (e.g., 10 minutes validity)
        if user.otp_generated_at and datetime.utcnow() - user.otp_generated_at > timedelta(minutes=10):
            flash('OTP has expired. Please request a new one.', 'danger')
            return redirect(url_for('main.register')) 
        if user.otp == form.otp.data:
            user.is_email_verified = True
            user.otp = None # Clear OTP after successful verification
            user.otp_generated_at = None
            db.session.commit()
            flash('Email verified successfully! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    return render_template('verify_otp.html', form=form, user_id=user.id)

@main.route('/resend_otp/<int:user_id>', methods=['POST'])
def resend_otp(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('main.login'))

    otp = generate_otp()
    user.otp = otp
    user.otp_generated_at = datetime.utcnow()
    db.session.commit()

    if send_otp_mail(user.email, otp):
        flash('A new OTP has been sent to your email.', 'success')
    else:
        flash('Failed to send new OTP. Please try again.', 'danger')
    return redirect(url_for('main.verify_otp', user_id=user.id))
        

@main.route('/login',methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password,form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('invalid credentials')
    return render_template('login.html',form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    total_members = FamilyMember.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html',total_members=total_members)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/members')
@login_required
def list_members():
    members = FamilyMember.query.filter_by(user_id=current_user.id).all()
    return render_template('members.html',members=members)

@main.route('/member/add', methods=['GET','POST'])
@login_required
def add_member():
    form = FamilyMemberForm()
    if form.validate_on_submit():
        member = FamilyMember(name=form.name.data,
                                  age=form.age.data,
                                  gender=form.gender.data,
                                  relation=form.relation.data,
                                  user_id=current_user.id)
        db.session.add(member)
        db.session.commit()
        flash('Family menber added')
        return redirect(url_for('main.list_members'))
    return render_template('add_member.html',form=form)

@main.route('/member/<int:member_id>')
@login_required
def view_member(member_id):
    member = FamilyMember.query.get_or_404(member_id)
    if member.user_id != current_user.id:
        flash('Unotherized')
        return redirect(url_for('main.list_members'))
    return render_template('view_member.html',member=member)

@main.route('/member/<int:member_id>/record/add', methods=['GET','POST'])
@login_required
def add_record(member_id):
    member= FamilyMember.query.get_or_404(member_id)
    if member.user_id != current_user.id:
        flash('Unotherized')
        return redirect(url_for('main.list_members'))
    
    form = HealthRecordForm()
    if form.validate_on_submit():
        record= HealthRecord(condition=form.condition.data,
                             medication=form.medication.data,
                             notes=form.notes.data,
                             date=form.date.data,
                             family_member_id=member.id)
        db.session.add(record)
        db.session.commit()
        flash('Record added')
        return redirect(url_for('main.view_member',member_id=member.id))
    return render_template('add_record.html',form=form,member=member)

@main.route('/member/<int:member_id>/delete',methods=['GET','POST'])
@login_required
def delete_member(member_id):
    member = FamilyMember.query.get(member_id)
    if current_user.id != member.user_id:
        flash('Unotherised')
        return redirect(url_for('main.home'))
    else:
        db.session.delete(member)
        db.session.commit()
        return redirect(url_for('main.list_members'))
    
@main.route('/edit/member/<int:member_id>',methods=['GET','POST'])
@login_required
def edit_member(member_id):
    member = FamilyMember.query.get(member_id)
    
    if not member:
        flash('Meber not found')
        return redirect(url_for('main.list_members'))
    if current_user.id != member.user_id:
        flash('Unautherized')
        return redirect(url_for('main.home'))
    form = FamilyMemberForm()

    if form.validate_on_submit():
        member.name = form.name.data
        member.age = form.age.data
        member.gender = form.gender.data
        member.relation = form.relation.data
        db.session.commit()
        flash('Member updated successfully')
        return redirect(url_for('main.list_members'))
    
    if request.method=='GET':
        form.name.data = member.name
        form.age.data = member.age
        form.gender.data = member.gender
        form.relation.data = member.relation

    return render_template('edit_member.html',form=form, member=member)

@main.route('/member/<int:member_id>/record')
@login_required
def view_records(member_id):
    member = FamilyMember.query.get_or_404(member_id)
    if member.user_id != current_user.id:
        flash('Unoutherized')
        return redirect(url_for('main.list_members'))
    records = HealthRecord.query.filter_by(family_member_id=member.id).all()
    return render_template('view_records.html',records=records,member=member)


@main.route('/record/<int:record_id>/edit',methods=['GET','POST'])
@login_required
def edit_record(record_id):
    record = HealthRecord.query.get_or_404(record_id)
    if record.member.user_id != current_user.id:
        flash('Unoutherized')
        return redirect('main.list_members')
    
    form = HealthRecordForm()
    if form.validate_on_submit():
        record.condition = form.condition.data
        record.medication = form.medication.data
        record.notes = form.notes.data
        record.date = form.date.data
        db.session.commit()
        flash('Record updated successfully')
        return redirect(url_for('main.view_records',member_id= record.family_member_id))
    
    return render_template('edit_record.html',form = form,record=record)

@main.route('/record/<int:record_id>/delete',methods=['POST'])
@login_required
def delete_record(record_id):
    record = HealthRecord.query.get_or_404(record_id)
    if record.member.user_id != current_user.id:
        flash('Unotherized')
        return redirect(url_for('main.list_members'))
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted')
    return redirect(url_for('main.view_records',member_id=record.family_member_id))

@main.route('/emergency')
@login_required
def emergency_mode():
    members = FamilyMember.query.filter_by(user_id=current_user.id).all()
    return render_template('emergency.html',members=members)


    
    

            

        
