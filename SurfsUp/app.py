# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime, timedelta 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-22"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago
    end_date_str = session.query(func.max(Measurement.date)).scalar()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    start_date = end_date - timedelta(days=365)

    # Query the precipitation data for the last 12 months
    results = session.query(
        Measurement.date,
        Measurement.prcp).filter(
        (func.strftime("%Y-%m-%d", Measurement.date) >= start_date), 
        (func.strftime("%Y-%m-%d", Measurement.date) <= end_date)
    ).all()

    session.close()

    # Convert results to a dictionary
    last_year = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        last_year.append(prcp_dict)

    return jsonify(last_year)

@app.route('/api/v1.0/stations')
def stations():
    # Query the stations
    results = session.query(Station.station).all()
    
    session.close() 
    # Convert results to a list
    stations_list = [station[0] for station in results]

    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
       # Create Dates
    end_date_str = session.query(func.max(Measurement.date)).scalar()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    start_date = end_date - timedelta(days=365)
    
    # Select most active station
    active_station = session.query(
        Measurement.station
    ).group_by(
        Measurement.station
    ).order_by(
        desc(func.count(Measurement.tobs))
    ).limit(1).scalar()
    
    #Create 12 month for most active station query
    results = session.query(
        Measurement.date,
        Measurement.tobs
    ).filter(
        (Measurement.station == active_station),
        (func.strftime("%Y-%m-%d", Measurement.date) >= start_date), 
        (func.strftime("%Y-%m-%d", Measurement.date) <= end_date)
    ).all()

    session.close()
    # Create a dictionary for most active query results
    active_year = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        active_year.append(tobs_dict)

# Jsonify data to be returned
    return jsonify(active_year)

# Create a dictionary for most active query results


@app.route('/api/v1.0/<start>')
def start(start):
    # Query the temperature statistics for a given start date
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    # Convert results to a dictionary
    temp_stats = {
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }

    return jsonify(temp_stats)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    # Query the temperature statistics for a given start and end date
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert results to a dictionary
    temp_stats = {
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)