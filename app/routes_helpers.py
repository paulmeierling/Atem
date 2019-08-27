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
    proximity_diff = np.diff(proximity) / np.diff(time_stamp)
    return time_stamp[np.argmax(proximity_diff)]

#Calculates moving average on data to smooth curve for taking differential 
def smooth_data(data, window=10):
    dataframe = pd.DataFrame(data).iloc[:,0].rolling(window).mean()
    return dataframe.fillna(dataframe.mean())

#Calculates breath flow rate based on pressure reading
def calculate_flow_rate(pressure):
    # Regression model: v = -18.26216 + (36.90) * P 
    flows = [-18.26 + 36.90*p for p in pressure] # (L/min)
    return flows

#### OLD HELPER FUNCTIONS FROM AVA NOT USED IN PRODUCTION ####

#Determines all the times that the user is breathing in 
def get_breath_in(time_stamp, pressure, window=10):
    # Compute moving average on pressure data
    pressure_rolling = smooth_data(pressure, window)

    # Take pressure differential and isolate inspiration times
    pressure_diff = np.diff(pressure_rolling.tolist()) / np.diff(time_stamp)
    # NOTE: maximum slope to be adjusted based on lab data 
    inflow = [1 if i<=-0.5 else 0 for i in pressure_diff]
    condensed_inflow = [0 for i in range(len(inflow))]
    last = None
    for i, val in enumerate(inflow):
        if val == 1 and last == None:
            last = i # last time of inspiration
        elif val == 1:
            # NOTE: number of data points merged to be adjusted based on lab data 
            if abs(i-last) <= 25:
                for j in range(last,i+1):
                    condensed_inflow[j] = 1
            last = i
    return condensed_inflow 

#Calculates the start and end of longest breath
def get_breath_duration(time_stamp, pressure, window=10):
    condensed_inflow = get_breath_in(time_stamp, pressure, window)
    start = None
    longest_stretch = (None,None) 
    for i, val in enumerate(condensed_inflow):
        if val == 1 and start == None:
            start = i
        elif val == 0 and start != None and longest_stretch[0] != None:
            if abs(start-(i-1)) > abs(longest_stretch[0]-longest_stretch[1]):
                longest_stretch = (start,i-1)
            start = None
        elif val == 0 and start != None:
            longest_stretch = (start,i-1)
            start = None
    print(time_stamp)
    # returns tuple of (start,end) times for inhalation duration
    return (time_stamp[longest_stretch[0]],time_stamp[longest_stretch[1]])

#Calcuate the average flow rate over inhalation stretch 
def get_average_flow(time_stamp, pressure, longest_stretch):
    # find indices in time_stamp for longest_stretch
    start_ind = time_stamp.index(longest_stretch[0])
    end_ind = time_stamp.index(longest_stretch[1])
    return np.mean(calculate_flow_rate(pressure[start_ind:end_ind+1]))

#Determine if actuation occurred during longest stretch on inhalation
#Expects a float and a tuple 
def get_coordination(actuation_time, longest_stretch):
    breath_start, breath_end = longest_stretch
    # return True if good coordination, else return False
    if breath_start < actuation_time  and actuation_time < breath_end:
        return True
    else:
        return False 