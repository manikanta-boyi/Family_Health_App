from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField,DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo


# creating Registratin form
class RegisterForm(FlaskForm):
    username = StringField('Enter username', validators=[DataRequired(),Length(min=3,max=30)])
    email = StringField('Enter your email',validators=[Email(),DataRequired()])
    password = PasswordField('Enter password',validators=[DataRequired(),Length(min=6),EqualTo('conf_password')])
    conf_password = PasswordField('Confirm password',validators=[DataRequired()])
    submit = SubmitField('submit')

# creating login form
class LoginForm(FlaskForm):
    email = StringField('Enter email',validators=[DataRequired(),Email()])
    password = PasswordField('Enter password',validators=[DataRequired()])
    submit = SubmitField('Login')


# Family menber form
class FamilyMemberForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    age = IntegerField('Age',validators=[DataRequired()])
    gender = StringField('Gender')
    relation = StringField('Relation to you')
    submit = SubmitField('save')

class HealthRecordForm(FlaskForm):
    condition = StringField('Condition',validators=[DataRequired()])
    medication = TextAreaField('Medication')
    notes = TextAreaField('Notes')
    date = DateField('Date',format= '%Y-%m-%d')
    submit = SubmitField('Save')