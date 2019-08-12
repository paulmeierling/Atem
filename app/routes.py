from app import app, db, s3
from flask import render_template, request, redirect, url_for
from app.models import Sensor_data    
from config import Config
import os, csv, random, datetime
import boto3
import numpy as np
#from itertools import compress
from routes_helpers import *

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
    pressure = [s.pressure for s in sensor_data]
    flow_rate = calculate_flow_rate(time_stamp, pressure)
    flow_rate_smooth = smooth_data(flow_rate, 10)

    return render_template("chart.html", time_stamp=time_stamp, pressure=pressure, proximity=flow_rate_smooth) 

@app.route('/inspiration/<collection_number>')
def inspiration(collection_number):
    sensor_data = Sensor_data.query.filter_by(collection_number=collection_number).all()
    time_stamp = [s.time_stamp for s in sensor_data]
    pressure = [s.pressure for s in sensor_data]
    rolling_pressure = smooth_data(pressure, 10)
    inspiration_time = get_breathe_in_time(time_stamp, pressure, 10)
    return render_template("chart.html", time_stamp=time_stamp, pressure=rolling_pressure, proximity=inspiration_time) 

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