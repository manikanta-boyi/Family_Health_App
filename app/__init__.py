from flask import Flask
from .routes import main
from .extensions import db, login_manager, migrate, mail
from app.models import User
from flask_mail import Mail
import os



app = Flask(__name__)


app.config['SECRET_KEY']='mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
app.config['SQLALCHEMY_DATABASE_TRACK_MODIFICATIONS']= False

app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587             
app.config['MAIL_USE_TLS'] = True         
app.config['MAIL_USE_SSL'] = False        
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER') 

app.register_blueprint(main)

db.init_app(app) # creating database tool
migrate.init_app(app,db)

login_manager.init_app(app)
login_manager.login_view = 'main.login'

mail.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))







