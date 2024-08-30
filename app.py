# Import the dependencies.
from flask import Flask, jsonify

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import pandas as pd

from datetime import datetime as dt, timedelta
#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# create app
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# index page
@app.route("/")
def index():
    return {"available routes":
            ["/",
            "/api/v1.0/precipitation",
            "/api/v1.0/stations",
            "/api/v1.0/tobs",
            "/api/v1.0/<start>",
            "/api/v1.0/<start>/<end>"]}

# precipitation data page
@app.route("/api/v1.0/precipitation")
def precipitation_view():
    # code copied directly from climate.ipynb
    res = session.query(func.max(Measurement.date)).first()
    most_recent_date = res[0]
    end_date = dt.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= end_date, Measurement.date <= most_recent_date)
    
    # iterate over precipitation_data, putting values into a dictionary containing the data on each row
    data = {}

    for date, precipitation in precipitation_data:
        data[date] = precipitation
    
    return jsonify(data)

# list of stations page
@app.route("/api/v1.0/stations")
def station_view():
    # getting all distinct stations from the Measurement table
    distinct_stations = session.query(Measurement.station).distinct()

    # loop through data, extracting each station's name and appending it to list of stations
    stations = []
    for station, *_ in distinct_stations:
        stations.append(station)

    # return list of stations
    return jsonify(stations)

# tobs data page
@app.route("/api/v1.0/tobs")
def tobs_view():
    # code copied directly from climate.ipynb
    most_active_id = 'USC00519281'

    end_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_id).first()[0]

    start_date = dt.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)

    temp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date <= end_date, Measurement.date >= start_date, Measurement.station == most_active_id)

    # loop through temp_data, adding date and observed temperature to data dictionary
    data = {}
    for date, temperature in temp_data:
        data[date] = temperature

    # return jsonified data dictionary
    return jsonify(data)

# create view just when start is specified
@app.route("/api/v1.0/<start>")
def start_only_view(start):

    # query for min, avd, and max temperatures for all data above the given start time
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).first()
    # add this data to a dictionary and return it
    data = {
        "TMIN": temp_data[0],
        "TAVG": temp_data[1],
        "TMAX": temp_data[2]
    }

    # return jsonified data
    return jsonify(data)

# create view when both start and end are specified
@app.route("/api/v1.0/<start>/<end>")
def start_end_view(start, end):

    # query for min, avg, and max temperatures for all data between the start and end time
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).first()
    # add this data to a dictionary and return it
    data = {
        "TMIN": temp_data[0],
        "TAVG": temp_data[1],
        "TMAX": temp_data[2]
    }

    # return jsonified data
    return jsonify(data)


# run app if it is the script that is being run
if __name__ == "__main__":
    app.run(debug=True)