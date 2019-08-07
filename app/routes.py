from app import app, db, s3
from flask import render_template, request, redirect, url_for
from app.models import Sensor_data    
from config import Config
import os, csv, random, datetime
import boto3
import numpy as np
from itertools import compress
import pandas as pd

#Returns the time when the actuation occurred based on the max gradient of proximity (may be off by 1 )
def get_actuation_time(time_stamp, proximity):
    #TO DO account for multiple actuations by looking at differentials that meet threshold?
    proximity_diff = np.diff(proximity) / np.diff(time_stamp)
    return time_stamp[np.argmax(proximity_diff)]

# Calculates breath flow rate based on pressure reading
def calculate_flow_rate(time_stamp, pressure):
    # Regression model: v = (1.51735241) * P + (-1529.15048679)
    flows = [((P*1.51735241)+(-1529.15048679))*60 for P in pressure] # (L/min)
    return flows

#Calculates the time a preson breathes in 
def get_breathe_in_time(time_stamp, pressure):
    # convert all pressure units from hPa to atm
    #pressure_atm = [hPa/1013.25 for hPa in pressure]
    # avergae based on the next 10? timepoints 
    P_0 = pressure_atm[0]
    pressure_diff = np.diff(pressure) / np.diff(time_stamp)
    
    flows = calculate_flow_rate(time_stamp, pressure)
    # subtract out starting flow rate 
    flows_norm = [x - flows[0] for x in flows]
    inflow = [1 if abs(flows_norm[i] > 1) and pressure_diff[i] < 0 else 0 for i in range(len(pressure_diff))]
    return inflow 
            
    #pressure = [p - 1013.25 for p in pressure]
    #inflow = [1 if (p < -4) else 0 for p in pressure]
    #return inflow

# Calculates the duration of breath 
def get_breathe_duration(time_stamp, pressure):
    pass

@app.route('/')
def index():
    collection_numbers = Sensor_data.query.with_entities(Sensor_data.collection_number).distinct()
    print(collection_numbers)
    collection_numbers = [c.collection_number for c in collection_numbers]
    return render_template("index.html", collection_numbers = collection_numbers)

@app.route('/flow_rate/<collection_number>')
def flow_rate(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure - 1013.25 for s in sensor_data] #Remove base pressure (1atm)
    flow_rate = calculate_flow_rate(time_stamp, pressure)
    return render_template("chart.html", time_stamp=time_stamp, pressure=pressure, proximity=flow_rate) 

@app.route('/show/<collection_number>')
def show(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure - 1013.25 for s in sensor_data] #Remove base pressure (1atm)
    proximity = [s.proximity for s in sensor_data]
    return render_template("chart.html", time_stamp=time_stamp, pressure=pressure, proximity=proximity) 

#Returns a graph of the proximity sensor and the differntiation of this graph 
@app.route('/show_diff/<collection_number>')
def show_diff(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    proximity = [s.proximity for s in sensor_data]  
    
    pressure_diff = np.diff(pressure) / np.diff(time_stamp) 
    pressure_diff = pressure_diff.tolist()
    proximity_diff = np.diff(proximity) / np.diff(time_stamp)
    proximity_diff = proximity_diff.tolist()

    return render_template("chart.html", time_stamp=time_stamp, pressure=[], proximity=proximity_diff) 

@app.route('/actuation_time/<collection_number>')
def actuation_time(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    proximity = [s.proximity for s in sensor_data]
    return str(get_actuation_time(time_stamp,proximity))


@app.route('/breathe_in_time/<collection_number>')
def breathe_in_time(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    breathe_in_time = get_breathe_in_time(time_stamp, pressure)
    return render_template("chart.html",time_stamp = time_stamp, pressure = breathe_in_time, proximity = [])



# Reads in POST request and writes the values in the database - deletes the current dataset at that collection number
@app.route('/write_sensor_data/<collection_number>', methods=['POST'])
def write_sensor_data(collection_number):
    # Delete any data which may be stored at the same dataspot
    Sensor_data.query.filter_by(collection_number=collection_number).delete() 

    for time_stamp in request.form:
        values = request.form[time_stamp].split(";")
        pressure = values[0]
        proximity = values[1]
        sensor_data = Sensor_data(collection_number=collection_number, time_stamp=time_stamp, pressure=pressure, proximity=proximity)
        db.session.add(sensor_data)
    db.session.commit()
    return str(request.form)

#Retrieve values from database 
@app.route('/retrive_db/<collection_number>')
def retrive_db(collection_number): 
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    return render_template('data.html', sensor_data = sensor_data)

#Deletes database 
@app.route('/delete_db')
def del_db(): 
    db.drop_all()
    return "Tables have been cleared"

#Downloads our whole dataset as csv file
@app.route('/download_csv')
def download_csv():
    filename = "mysql_dump.csv"
    if url_for('static', filename=filename):
        return redirect(url_for('static', filename=filename))
    else:
        return "Database currently not available"

#Writes the whole database as CSV file 
@app.route('/write_database_as_csv')
def write_database_as_csv():
    #Write local csv file 
    filename = "database_dump.csv"
    path = os.path.join(Config.APP_ROOT, "app/static", filename)
    csv_file = open(path,'w+')
    data = Sensor_data.query.all()
    for row in data:
        row_as_string = str(row)
        csv_file.write(row_as_string + '\n')
    csv_file.close()

    #Opload file to AWS S3
    with open(path,"rb") as s3_file:
        s3_filename = str(datetime.datetime.now()) + "database_dump.csv"
        s3.upload_fileobj(s3_file, app.config["S3_BUCKET"], s3_filename)
    
    return "File is available under: {}{}".format(app.config["S3_LOCATION"], s3_filename)

@app.route('/version')
def version():
    return "v0.8"
