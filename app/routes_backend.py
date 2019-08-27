from app import app, db, s3
from flask import render_template, request, redirect, url_for
from app.models import Sensor_data, Run_summary    
from config import Config
import datetime, random, os
from decimal import Decimal
from app.routes_helpers import breath_timing, get_actuation_time, get_average_flow, get_coordination, calculate_flow_rate


# Reads in POST request and writes the values in the database - deletes the current dataset at that collection number
@app.route('/sensor_data/<summary_id>', methods=['GET','PUT'])
def sensor_data(summary_id):
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
        
        actuation_time = 0 #NOTE: To be changed once we measure actuation again
        max_inflow = min(calculate_flow_rate(pressure))

        good_coordination = False
        shaken = False
        breath_time = breath_timing(time_stamp, pressure)
        start_breath = breath_time[0]
        end_breath = breath_time[1]

        #start_breath, end_breath = get_breath_duration(time_stamp, pressure)
        #good_coordination = get_coordination(actuation_time, longest_stretch)
        #longest_stretch = (start_breath, end_breath)
        #max_inflow = get_average_flow(time_stamp, pressure, longest_stretch)


        run_summary = Run_summary(id=summary_id, datetime=datetime.datetime.now(), actuation_time=actuation_time, shaken=shaken, max_inflow=max_inflow, start_breath=start_breath, end_breath=end_breath, good_coordination=good_coordination)
        db.session.merge(run_summary) #Merge - updates the object if it already exists

        #3. Create sensor_data object with the actual sensor data
        Sensor_data.query.filter_by(summary_id=summary_id).delete() #Delete existing data for this run
        for i in range(0,len(time_stamp)):
            sensor_data = Sensor_data(summary_id=summary_id, time_stamp=time_stamp[i], pressure=pressure[i], proximity=proximity[i])
            db.session.add(sensor_data)
        db.session.commit()
        return "Sensor data has been written to database"

    #GET REQUEST RETURNS THE RELEVANT SENSOR DATA
    if request.method == 'GET':
        sensor_data = Sensor_data.query.filter_by(summary_id=summary_id).all()
        response_data = {}
        for s in sensor_data:
            response_data[s.time_stamp] = [s.pressure, s.proximity]
        return response_data


@app.route('/run_summaries/<summary_id>', methods=['GET','PUT'])
def actuation_data(summary_id):
    if request.method == 'GET':
        rs = Run_summary.query.filter_by(id=summary_id).first()
        response_data = {"Date" : rs.datetime, "Inflow_rate" : rs.max_inflow, "Start_breath" : rs.start_breath, "End_breath" : rs.end_breath, "Actuation_time": rs.actuation_time, "Shaken" : rs.shaken, "Coordination": rs.good_coordination}
        return response_data
        
    if request.method == 'PUT':
        return "To be implemented"

@app.route('/get_last_run', methods=['GET'])
def get_last_run():
    rs = Run_summary.query.order_by(Run_summary.id.desc()).first()
    response_data = {"Id":rs.id, "Date" : rs.datetime, "Inflow_rate" : rs.max_inflow, "Start_breath" : rs.start_breath, "End_breath" : rs.end_breath, "Actuation_time": rs.actuation_time, "Shaken" : rs.shaken, "Coordination": rs.good_coordination}
    return response_data


#Deletes database 
@app.route('/clear_db')
def clear_db(): 
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        db.session.execute(table.delete())
    db.session.commit()
    return "Database values have been cleared"


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
        s3_filename = "database_dump.csv"
        s3.upload_fileobj(s3_file, app.config["S3_BUCKET"], s3_filename, ExtraArgs={'ACL':'public-read'})
    return "File is available under: {}{}".format(app.config["S3_LOCATION"], s3_filename)

@app.route('/version')
def version():
    return "v1.0"