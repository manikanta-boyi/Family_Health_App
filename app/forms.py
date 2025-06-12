from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo


# creating Registratin form
class RegisterForm(FlaskForm):
    username = StringField('Enter username', validators=[InputRequired(),Length(min=3,max=30)])
    email = StringField('Enter your email',validators=[Email(),InputRequired()])
    password = PasswordField('Enter password',validators=[InputRequired(),Length(min=6),EqualTo('conf_password')])
    conf_password = PasswordField('Confirm password',validators=[InputRequired()])
    submit = SubmitField('submit')

# creating login form
class LoginForm(FlaskForm):
    email = StringField('Enter email',validators=[InputRequired(),Email()])
    password = PasswordField('Enter password',validators=[InputRequired()])
    submit = SubmitField('Login')