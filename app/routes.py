import random
from app import app, db
from flask import render_template, request, redirect, url_for
from app.forms import LoginForm
from app.models import Pressure_data    
import pandas as pd

@app.route('/')
def index():
    return redirect(url_for('show', collection_number=1))

@app.route('/show/<collection_number>')
def show(collection_number):
    pressure_data = Pressure_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [p.time_stamp for p in pressure_data]
    pressure = [p.pressure - 1008 for p in pressure_data]
    temperature = [p.temperature for p in pressure_data]
    return render_template("chart.html", time_stamp=time_stamp, pressure=pressure, temperature=temperature)


# Reads in POST request and writes the values in the database 
# Expects a JSON file in the body of the post request
@app.route('/write_sensor_data/<collection_number>', methods=['POST'])
def write_sensor_data(collection_number):
    for time_stamp in request.form:
        values = request.form[time_stamp].split(";")
        pressure = values[0]
        temperature = values[1]
        pressure_data = Pressure_data(collection_number=collection_number, time_stamp=time_stamp, pressure=pressure, temperature = temperature)
        db.session.add(pressure_data)
    db.session.commit()
    return str(request.form)

#Retrieve values from database 
@app.route('/retrive_db/<collection_number>')
def retrive_db(collection_number): 
    pressure_data = Pressure_data.query.filter_by(collection_number=collection_number).all()
    return render_template('data.html', pressure_data = pressure_data)

@app.route('/reset_db')
def reset_db():
    db.drop_all()
    db.create_all()
    df = pd.read_csv("sensor_data.csv", header = None, names=["Time","Pressure"])
    for _, row in df.iterrows():
        time_stamp = row["Time"].tolist()
        pressure = row['Pressure'].tolist()
        temperature = random.uniform(25,27)
        pressure_data = Pressure_data(collection_number=1, time_stamp=time_stamp, pressure=pressure, temperature=temperature)
        db.session.add(pressure_data)
    db.session.commit()
    return "Database has been populated"

#Deletes database 
@app.route('/del_db')
def del_db(): 
    db.drop_all()
    return "Tables have been dropped"


@app.route('/version')
def version():
    return "v0.4"