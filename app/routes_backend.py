from app import app, db, s3
from flask import render_template, request, redirect, url_for
from app.models import Sensor_data, Run_summary    
from config import Config
import os, csv, random, datetime
import boto3
from app.routes_helpers import get_breath_duration


# Reads in POST request and writes the values in the database - deletes the current dataset at that collection number
@app.route('/sensor_data/<actuation_id>', methods=['GET','PUT'])
def sensor_data(actuation_id):
    #PUT REQUEST CREATES NEW RUN_SUMMARY AND SENSOR DATA 
    if request.method == 'PUT':
        #1. Unpack the request.form to fill the three arrays with the values that the sensor has send 
        time_stamp = []
        pressure = []
        proximity = []
        for key in request.form:
            values = request.form.getlist(key)
            time_stamp.append(float(key))
            pressure.append(float(values[0]))
            proximity.append(float(values[1]))
        
        #2. Create Run_summary object with the values 
        start_breath, end_breath = get_breath_duration(time_stamp,pressure)
        run_summary = Run_summary(id=actuation_id, datetime=datetime.datetime.now(), actuation_time=1, avg_inflow=1, start_breath=start_breath, end_breath=end_breath)
        db.session.merge(run_summary) #Merge updates the object if it already exists 

        #3. Create sensor_data object with the actual sensor data 
        Sensor_data.query.filter_by(actuation_id=actuation_id).delete() #Delete existing data for this run
        for i in range(0,len(time_stamp)):
            sensor_data = Sensor_data(actuation_id=actuation_id, time_stamp=time_stamp[i], pressure=pressure[i], proximity=proximity[i])
            db.session.add(sensor_data)
        db.session.commit()
        return "Sensor data has been written to database"

    #GET REQUEST RETURNS THE RELEVANT SENSOR DATA
    if request.method == 'GET':
        sensor_data = Sensor_data.query.filter_by(actuation_id=actuation_id).all()
        response_data = {}
        for s in sensor_data:
            response_data[s.time_stamp] = [s.pressure, s.proximity]
        return response_data


@app.route('/run_summaries/<summary_id>', methods=['GET','PUT'])
def actuation_data(actuation_id):
    if request.method == 'GET':
        rs = Run_summary.query.filter_by(id=actuation_id).first()
        response_data = {"Date" : rs.datetime, "Inflow rate" : rs.avg_inflow, "Start breath" : rs.start_breath, "End breath" : rs.end_breath, "Actuation time": rs.actuation_time}
        return response_data
        


    if request.method == 'PUT':
        return "To be implemented"


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