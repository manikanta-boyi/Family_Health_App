from .extensions import db
from flask_login import UserMixin


# creating model(Table) for user
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100),unique=True,nullable=False)
    email = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(200),nullable=False)


# Family member Model
class FamilyMember(db.Model):
    __tablename__ = "family_member"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    age = db.Column(db.Integer,nullable=False)
    gender = db.Column(db.String(10))
    relation = db.Column(db.String(50))

    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    records = db.relationship('HealthRecord',backref='member',lazy=True)

class HealthRecord(db.Model):
    __tablename__ = "health_record"
    id = db.Column(db.Integer,primary_key=True)
    condition = db.Column(db.String(100),nullable=False)
    medication = db.Column(db.Text)
    notes = db.Column(db.Text)
    date = db.Column(db.Date)

    family_member_id = db.Column(db.Integer,db.ForeignKey('family_member.id'),nullable = False)