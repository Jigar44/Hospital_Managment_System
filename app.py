import json
from datetime import datetime
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
from models import User, Patient

migrate = Migrate(app, db)

db.engine.execute("ALTER TABLE userstore AUTO_INCREMENT = 100000001;")
db.engine.execute("ALTER TABLE patients AUTO_INCREMENT = 100000001;")


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                user.logged_in = datetime.now()
                db.session.commit()
                session['username'] = user.username
                session['role'] = user.role
                if session['role'] == 'admin':
                    return redirect('/admin')
                if session['role'] == 'pharmacist':
                    return redirect('/pharmacist')
                if session['role'] == 'diagnostic':
                    return redirect('/diagnostic')
                return redirect(url_for('login'))
            else:
                flash('Username and password combination does not match', 'danger')
    else:
        if request.method == 'GET':
            if session.get('role') == 'admin':
                return redirect('/admin')
            elif session.get('role') == 'pharmacist':
                return redirect('/pharmacist')
            elif session.get('role') == 'diagnostic':
                return redirect('/diagnostic')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if username and password and role:
            user = User.query.filter_by(username=username).first()
            if user is None:
                user = User(username=username, role=role)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash('You have successfully registered! You may now login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('User already exists', 'danger')
    else:
        if session.get('username'):
            return redirect(url_for('login'))
    return render_template('register.html')


# ==========Admin=========================
@app.route('/admin')
@app.route('/admin/home')
def adminHome():
    if request.method == 'GET' and session.get('username'):
        return render_template('admin/home.html')
    else:
        return redirect(url_for('login'))


@app.route('/admin/create_patient', methods=['POST', 'GET'])
def create_patient():
    p_message = "Patient Created successfully!"
    if session.get('username') and session.get('role') == 'admin':
        with open('static/state_city.json') as datafile:
            data = json.load(datafile)
        if request.method == 'POST':
            ssnid = request.form['ssnid']
            pname = request.form['pname']
            age = request.form['age']
            address = request.form['address']
            skey = int(request.form['state'])
            ckey = int(request.form['city'])
            state = data['states'][skey]['state']
            city = data['states'][skey]['city'][ckey]
            bedtype = request.form['bedtype']
            admitdate = request.form['admitdate']
            if ssnid and pname and age and address and state and city and bedtype and admitdate:
                patient = Patient.query.filter_by(ssnid=ssnid).first()
                if patient is None:
                    patient = Patient(ssnid=ssnid, pname=pname, age=age, address=address, state=state, city=city,
                                      bedtype=bedtype, admitdate=admitdate)
                    db.session.add(patient)
                    db.session.commit()
                    flash(p_message, "success")
                else:
                    flash("Patient with SSN ID : " + ssnid + " already exists!", "warning")
                return render_template('admin/create_patient.html', data=data)
        elif request.method == 'GET':
            return render_template('admin/create_patient.html', data=data)
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))


@app.route('/admin/all_active_patients', methods=['GET', 'POST'])
def all_active_patients():
    if session.get('username') and session.get('role') == 'admin' and request.method == 'GET':
        print('Hello')
        all_active_patients_list = Patient.query.filter_by(pstatus='active').all()
        print('All Patients',all_active_patients_list)
        if all_active_patients_list:
            return render_template('admin/all_active_patients.html', data=all_active_patients_list)
        else:
            flash("There is No Active Patients.", 'danger')
            return render_template('admin/home.html')
    return render_template('admin/all_active_patients.html')


@app.route('/pharmacist')
@app.route('/pharmacist/home')
def pharmacistHome():
    if request.method == 'GET' and session.get('username'):
        return render_template('pharmacist/home.html')
    else:
        return redirect(url_for('login'))


@app.route('/diagnostic')
@app.route('/diagnostic/home')
def diagnosticHome():
    if request.method == 'GET' and session.get('username'):
        return render_template('diagnostic/home.html')
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
