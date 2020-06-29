from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event,DDL

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



event.listen(User.__table__,"after_create",
DDL(" ALTER TABLE %(table)s AUTO_INCREMENT = 100000001;")
)


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

event.listen(Patient.__table__,
    "after_create",
    DDL("""
    ALTER TABLE %(table)s AUTO_INCREMENT = 100000001;
    """)
)

class MedicineDetails(db.Model):
    __tablename__ = 'medicine_details'

    medid = db.Column(db.Integer, primary_key=True)
    medname = db.Column(db.String(100), nullable=False,unique=True)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Numeric(10,4), nullable=False)
    created_on = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_on = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now(), onupdate=datetime.now())

# event.listen(
#     MedicineDetails.__table__,
#     "after_create",
#     DDL("""
#     ALTER TABLE %(table)s AUTO_INCREMENT = 100000001;
#     """)
# )

db.create_all()
db.session.commit()