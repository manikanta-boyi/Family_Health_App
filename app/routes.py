from flask import Blueprint,render_template, flash, redirect, url_for,request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required, current_user, logout_user

from .forms import RegisterForm, LoginForm, FamilyMemberForm, HealthRecordForm
from app.extensions import db,login_manager

from .models import User, FamilyMember, HealthRecord

main = Blueprint('main',__name__)




@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register',methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data,email=form.email.data,password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created succesfully')
        return redirect(url_for('main.login'))
    return render_template('register.html',form=form)

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
    return render_template('dashboard.html')

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
    member = FamilyMember.query.get(id=member_id)
    
    if not member:
        flash('Meber not found')
        return redirect(url_for('main.list_members'))
    if current_user.id != member.user_id:
        flash('Unautherized')
        return redirect('main.home')
    form = FamilyMemberForm()

    if form.validate_on_submit():
        member.name = form.name.data
        member.age = form.age.data
        member.gender = form.gender.data
        member.relation = form.relation.data
        db.session.commit()
        flash('Member updated successfully')
        return redirect(url_for('main.members'))
    
    if request.method=='GET':
        form.name.data = member.name
        form.age.data = member.age
        form.gender.data = member.gender
        form.relation.data = member.relation

    return render_template('edit_member.html',form=form)

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
    
    return render_template('edit_record.html',form = form)

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


    
    

            

        
