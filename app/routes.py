from app import app, db, s3
from flask import render_template, request, redirect, url_for
from app.forms import LoginForm
from app.models import Pressure_data    
from config import Config
import os, csv, random, datetime
import boto3


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

#Deletes database 
@app.route('/delete_db')
def del_db(): 
    db.drop_all()
    return "Tables have been dropped"

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
    data = Pressure_data.query.all()
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
    return "v0.6"
