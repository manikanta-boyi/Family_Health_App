from flask import Flask
from .routes import main


app = Flask(__name__)

app.config['SECRET_KEY']='mysecretkey'

app.register_blueprint(main)






