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
    actuation_ids = [run_summary.id for run_summary in summaries]
    return render_template("index.html", actuation_ids = actuation_ids)

@app.route('/show/<actuation_id>')
def show(actuation_id):
    sensor_data = Sensor_data.query.filter_by(actuation_id=actuation_id).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure - 1013.25 for s in sensor_data] #Remove base pressure (1atm)
    proximity = [s.proximity for s in sensor_data]
    return render_template("chart.html", x_values=time_stamp, y1_values=pressure, y2_values=proximity) 

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

@app.route('/actuation_time/<actuation_id>')
def actuation_time(actuation_id):
    sensor_data = Sensor_data.query.filter_by(actuation_id=actuation_id).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    proximity = [s.proximity for s in sensor_data]
    return str(get_actuation_time(time_stamp,proximity))

########################
### Sensor database ####
########################

# Also NAN values
@app.route('/flow_rate/<collection_number>')
def flow_rate(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    flow_rate = calculate_flow_rate(time_stamp, pressure)
    flow_rate_smooth = smooth_data(flow_rate, 10)
    return render_template("chart.html", x_values=time_stamp, y1_values=pressure, y2_values=flow_rate_smooth) 

#Currently has NAN values
@app.route('/inspiration/<collection_number>')
def inspiration(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    rolling_pressure = smooth_data(pressure, 10)
    inspiration_time = get_breathe_in_time(time_stamp, pressure, 10)
    return render_template("chart.html", x_values=time_stamp, y1_values=rolling_pressure, y2_values=inspiration_time) 

@app.route('/breathe_in_time/<collection_number>')
def breathe_in_time(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    breathe_in_time = get_breathe_in_time(time_stamp, pressure)
    return render_template("chart.html",time_stamp = time_stamp, pressure = breathe_in_time, proximity = [])
