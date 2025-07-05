from flask import Flask
from models import db, Member, Trail, Signup, Waiver, HikersHistory, HikesHistory, Vehicle, Log

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace-this-with-a-real-secret'
app.config['SQLALCHEMY_DATABASE_URI']   = 'sqlite:///hikeuci.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)

with app.app_context():
    db.create_all()

@app.after_request
def log_request(response):
    pass