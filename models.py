from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'userstore'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(15))
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    logged_in = db.Column(db.TIMESTAMP, nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Patient(db.Model):
    __tablename__ = 'patients'

    pid = db.Column(db.Integer, primary_key=True)
    ssnid = db.Column(db.Integer, index=True, unique=True)
    pname = db.Column(db.String(60), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(300), nullable=False)
    state = db.Column(db.String(60), nullable=False)
    city = db.Column(db.String(60), nullable=False)
    bedtype = db.Column(db.String(15), nullable=False)
    pstatus = db.Column(db.String(10), nullable=False, default='active')
    admitdate = db.Column(db.Date, default=datetime.now())
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_on = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now(), onupdate=datetime.now())