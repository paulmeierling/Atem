from app import app, db, s3
from flask import render_template, request, redirect, url_for
from app.models import Sensor_data, Run_summary    
from config import Config
import os, csv, random, datetime
import boto3
import numpy as np
#from itertools import compress
from app.routes_helpers import *

##########################
### Run_summary database ###
##########################

@app.route('/')
def index():
    summaries = Run_summary.query.all()
    summary_ids = [run_summary.id for run_summary in summaries]
    return render_template("index.html", summaries = summaries)

@app.route('/show/<summary_id>')
def show(summary_id):
    sensor_data = Sensor_data.query.filter_by(summary_id=summary_id).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure - 1013.25 for s in sensor_data] #Remove base pressure (1atm)
    proximity = [s.proximity for s in sensor_data]
    flow_rate = calculate_flow_rate(pressure)
    return render_template("chart.html", x_values=time_stamp, y1_values=flow_rate, y2_values=proximity) 

################# OLD AND NOT NEEDED ANYMORE ######### 
#Returns a graph of the proximity sensor and the differntiation of this graph 
@app.route('/show_diff/<actuation_id>')
def show_diff(actuation_id):
    sensor_data = Sensor_data.query.filter_by(actuation_id=actuation_id).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    proximity = [s.proximity for s in sensor_data]  
    
    pressure_diff = np.diff(pressure) / np.diff(time_stamp) 
    pressure_diff = pressure_diff.tolist()
    proximity_diff = np.diff(proximity) / np.diff(time_stamp)
    proximity_diff = proximity_diff.tolist()

    return render_template("chart.html", x_values=time_stamp, y1_values=[], y2_values=proximity_diff) 

########################
### Sensor database ####
######################## 

#Currently has NAN values
@app.route('/breathe_in_time/<actuation_id>')
def breathe_in_time(actuation_id):
    sensor_data = Sensor_data.query.filter_by(actuation_id=actuation_id).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    breathe_in = get_breath_in(time_stamp, pressure)
    print(breathe_in)
    return render_template("chart.html",time_stamp = time_stamp, pressure = breathe_in, proximity = [])

@app.route('/average_inflow/<actuation_id>')
def average_inflow(actuation_id):
    sensor_data = Sensor_data.query.filter_by(actuation_id=actuation_id).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    longest_stretch = get_breath_duration(time_stamp, pressure)
    return str(get_average_flow(time_stamp, pressure, longest_stretch))
