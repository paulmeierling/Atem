from app import app, db, s3
from flask import render_template, request, redirect, url_for
from app.models import Sensor_data    
from config import Config
import os, csv, random, datetime
import boto3

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