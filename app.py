# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///..//Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app =Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    """All available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Replace 'start' and 'end' with dates in yyyy-mm-dd format:<br/>"
        f"/api/v1.0/start/<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the results of the precipitation analysis for the last 12 months"""
    session = Session(engine)
    start_date = '2016-08-23'
    end_date = '2017-08-23'
    precipitation_results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= start_date, measurement.date <= end_date).all()
    session.close()

      # Convert the list to Dictionary
    all_precipitation = [{"date": date, "prcp": prcp} for date, prcp in precipitation_results]

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query to retrieve all station data
    stations_data = session.query(station.name, station.station, station.elevation, station.latitude, station.longitude).all()
    session.close()

    # Format the results as a list of dictionaries
    stations_results = [{"name": name, "station": station, "elevation": elevation, "latitude": latitude, "longitude": longitude}\
                    for name, station, elevation, latitude, longitude in stations_data]

    ordered_stations_results = [OrderedDict(sorted(station_info.items(), key=lambda\
                                                    item: ["name", "station", "elevation", "latitude", "longitude"].index(item[0]))) for station_info in stations_results]

    return jsonify(ordered_stations_results)

@app.route("/api/v1.0/tobs")
def observations():
    def tobs():
        session = Session(engine)
        start_date = '2016-08-23'
        end_date = '2017-08-23'
        top_station = session.query(measurement.station).\
                    group_by(measurement.station).\
                    order_by(func.count(measurement.station).desc()).subquery()

        tobs_results = session.query(measurement.date, measurement.tobs).\
                filter(measurement.date >= start_date, measurement.date <= end_date).all()
        session.close()

        # Convert the list to Dictionary
        top_tobs_station = [{"date": date, "tobs": tobs} for date, tobs in tobs_results]

        return jsonify(top_tobs_station)


# Dynamic Routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start = None, end = None):
    session = Session(engine)
    
    # Make a list to query (the minimum, average and maximum temperature)
    sel=[func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    # Find out if there's an end date 
    if end == None: 
        # Query the data from start date to the most recent date
        start_data = session.query(*sel).filter(measurement.date >= start).all()
        
        # Convert list of tuples into normal list
        start_list = [item for sublist in start_data for item in sublist]
        return jsonify(start_list)
    
    else:
        # Query the data from start date to the end date
        start_end_data = session.query(*sel).filter(measurement.date >= start).\
            filter(measurement.date <= end).all()
        # Convert list of tuples into normal list 
        start_end_list = [item for sublist in start_end_data for item in sublist]

        return jsonify(start_end_list)           
    
# Close the session
session.close()

# Define main behavior
if __name__ == '__main__':
    app.run(debug=True)