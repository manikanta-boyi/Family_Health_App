from flask import Flask
from .routes import main
from .extensions import db, login_manager, migrate, mail, jwt
from app.models import User
from flask_mail import Mail
import os
from flask_jwt_extended import JWTManager,jwt_required,create_access_token,create_refresh_token
from datetime import timedelta
from .api import api


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

app.config['JWT_SECRET_KEY']='QWPFEUGIRVOIEj1352514726yfljkdgah;d'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15) #Access tokens valid for 15 minutes
app.config['JWT_REFRESH_TOKEN_EXPIRES']= timedelta(days=30) #refresh tokens valid for 30 days



app.register_blueprint(main)
app.register_blueprint(api)

db.init_app(app) # creating database tool
migrate.init_app(app,db)

login_manager.init_app(app)
login_manager.login_view = 'main.login'

mail.init_app(app)
jwt.init_app(app)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))







