import json
from datetime import datetime
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
from models import User, Patient,MedicineDetails

migrate = Migrate(app, db)



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
    if session.get('role')=='admin':
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
    if session.get('username') and session.get('role') == 'admin':
        if request.method == 'GET':
            all_active_patients_list = Patient.query.filter_by(pstatus='active').all()
            if all_active_patients_list:
                return render_template('admin/all_active_patients.html', data=all_active_patients_list)
            else:
                flash("There is No Active Patients.", 'danger')
                return render_template('admin/home.html')
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))




@app.route('/admin/search_patients',methods=['GET', 'POST'])
def search_patients():
    
    if session.get('username') and session.get('role') == 'admin' or 'pharmacist' or 'diagnostic':
    
        if request.method == 'POST':
    
            if('ssnid'in request.form):
                id=request.form['ssnid']
                patient=Patient.query.filter_by(ssnid=id).first()
            elif('pid'in request.form):
                id=request.form['pid']
                patient=Patient.query.filter_by(pid=id).first()
            if patient!=None:
                flash("Patient Found!")
                return render_template('admin/search_patients.html',data=patient)
            else:
                flash('No patient with ID : '+id + " found in the records!")    
        return render_template('admin/search_patients.html')
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))

@app.route('/admin/update',methods=['GET','POST'])
def update():
    if session.get('username') and session.get('role') == 'admin':
        if request.method == 'POST':
            print("Request SSNID is : ",request.form['ssnid'])
            return "Update hello : "+request.form['ssnid']
        return redirect(url_for('search_patients'))
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))

@app.route('/admin/delete',methods=['GET','POST'])
def delete():
    if session.get('username') and session.get('role') == 'admin':
        if request.method == 'POST':
            ssnid=request.form['ssnid']
            patient=Patient.query.filter_by(ssnid=ssnid).first()
            db.session.delete(patient)
            db.session.commit()
            flash("Patient: ID-{} | Name-{} , deleted succefully!".format(patient.ssnid,patient.pname))    
        return redirect(url_for('search_patients'))
    else:
        flash("Login first as a Desk Executive", "danger")
        return redirect(url_for('login'))        

# ========Pharmacist============
@app.route('/pharmacist')
@app.route('/pharmacist/home')
def pharmacistHome():
    if session.get('role')=='pharmacist':
        return render_template('pharmacist/home.html')
    else:
        return redirect(url_for('login'))

@app.route('/pharmacist/search_patients',methods=['GET','POST'])
def pharma_search_patients():
    if session.get('role')=='pharmacist':
        return search_patients()
    else:
        return redirect(url_for('login'))


@app.route('/pharmacist/resupply',methods=['GET','POST'])
def resupply_medicines():
    if session.get('role')=='pharmacist':
        if request.method=='POST':
            if request.form['submit']=='add':
                # print('here add')
                medid=request.form['addmedid']
                medname=request.form['addmedname']
                medicine=MedicineDetails.query.filter(or_(MedicineDetails.medid==medid,MedicineDetails.medname.like(medname))).all()
                # print("Med : ",medicine)
                quantity=request.form['addquantity']
                rate=request.form['addrate']
                # Avoiding duplicate entries
                if not medicine:
                    medicine=MedicineDetails(medid=medid,medname=medname,quantity=quantity,rate=rate)
                    db.session.add(medicine)
                    db.session.commit()
                    flash("New Medicine added succefully!")
                else:
                    flash("Medicine with Id : {} or Name: {} ,already exist, use update quantity to resupply!".format(medid,medname))
            elif request.form['submit']=='update':
                medid=request.form['updatemedid']
                quantity=int(request.form['updatequantity'])
                print("in update med")
                medicine=MedicineDetails.query.filter_by(medid=medid).first()
                medicine.quantity+=quantity
                db.session.commit()
                flash("Medicine Id : {},Quantity updated to : {}".format(medid,medicine.quantity))
        medicine=MedicineDetails.query.filter().all()
        return render_template('pharmacist/resupply.html',med_data=medicine)
    else:
        return redirect(url_for('login'))



# ========Diagnostic============
@app.route('/diagnostic')
@app.route('/diagnostic/home')
def diagnosticHome():
    if request.method == 'GET' and session.get('role')=='diagnostic':
        return render_template('diagnostic/home.html')
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
