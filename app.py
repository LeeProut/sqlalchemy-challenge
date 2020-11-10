
#import dependencies 
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#import Flask
from flask import Flask, jsonify

#database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

#test connection to database by printing classes
#print(Base.classes.keys())

#set variable for each class
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# #create app
app = Flask(__name__)

#define homepage
#list all routes that are available
@app.route("/")
def index():
    return """
        Available Routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/<start>yyyy-mm-dd<br>
        /api/v1.0/<start>/<end>yyyy-mm-dd/yyyy-mm-dd<br/>
    """

# #Convert the 12 months of precip data query results to a dictionary 
# #using date as the key and prcp as the value.
# #Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return a list of precipitation data, including date and precipitation measurement"""
    #Query precipitation data
    #results = session.query(Measurement.date, Measurement.prcp).all()

    #find date 1 year ago from last data point in the database
    session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    query_date

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= query_date).all()

    precipitation = []
    for date, prcp in results: 
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation)

# #Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")  
def stations():

    """Return a list of station IDs and station names"""
    #Query station table 
    results = session.query(Station.station, Station.name).all()

    stations = []
    for station, name in results: 
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        stations.append(station_dict)

    return jsonify(stations)    

# #Query the dates and temperature observations 
# #of the most active station for the last year of data.
# #Return a JSON list of temperature observations (TOBS) 
# #for the previous year.
@app.route("/api/v1.0/tobs")
def active_temps():

    """Return a list of the temp observations for the most active station for the last year of data"""
    #Query measurement table
    # Calculate the date 1 year ago from the last data point in the database
    query_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    format_query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)


    #find the station with the highest number of temp observations
    most_temps = session.query(Measurement.station, func.count(Measurement.tobs))\
                                .group_by(Measurement.station)\
                                .order_by(func.count(Measurement.tobs).desc())\
                                .first()
    #set variable for the id of the station
    most_temps_id = most_temps[0]

    #query the last 12 months of temp observation data for this station
    results = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= format_query_date).\
                    filter(Measurement.station == most_temps_id).\
                    order_by(Measurement.date).all()

    temps = []
    for station, tobs in results: 
        temps_dict = {}
        temps_dict["Station ID"] = station
        temps_dict["Temperature"] = tobs
        temps.append(temps_dict)

    return jsonify(temps)

   
# #Return a JSON list of the minimum temperature, the average temperature, 
# #and the max temperature for a given start or start-end range.

# #When given the start only, calculate TMIN, TAVG, and TMAX 
# #for all dates greater than and equal to the start date.

# #When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
# #for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def date_temps(start):

    """Return a list of min, avg, and max temp for a user defined start date"""

#calculate tmin, tavg, and tmax for all dates greater than the start date
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()

    date_temps = []   
    for temps in results: 
        dt_dict = {}
        dt_dict["Min Temp"] = temps[1] 
        dt_dict["Avg Temp"] = temps[2]
        dt_dict["Max Temp"] = temps[3]   
        date_temps.append(dt_dict) 

    return jsonify(date_temps)            

@app.route("/api/v1.0/<start>/<end>")
def date_range_temps(start, end):
   

    """Return a list of min, avg, and max temp for a user defined start and end date"""

#calculate tmin, tavg, and tmax for dates between the start and end date
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()

    session.close()

    date_range_temps = []   
    for temps in results: 
        dt_range_dict = {}
        dt_range_dict["Min Temp"] = temps[1] 
        dt_range_dict["Avg Temp"] = temps[2]
        dt_range_dict["Max Temp"] = temps[3]   
        date_range_temps.append(dt_range_dict) 

    return jsonify(date_range_temps)            

if __name__ == "__main__":
    app.run(debug=True)

