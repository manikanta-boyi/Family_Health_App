from flask import Flask
from .routes import main
from .extensions import db, login_manager, migrate
from app.models import User



app = Flask(__name__)


app.config['SECRET_KEY']='mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SQLALCHEMY_DATABASE_TRACK_MODIFICATIONS']= False

app.register_blueprint(main)

db.init_app(app) # creating database tool
migrate.init_app(app,db)

login_manager.init_app(app)
login_manager.login_view = 'main.login'



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))







