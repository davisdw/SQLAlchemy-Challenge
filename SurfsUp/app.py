# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Station = Base.classes.station
Measurements = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
last_twelve_months = '2016-08-23'

@app.route("/")
def welcome_page():

    return(
    
            f"<h1>Welcome to the Hawaii Weather!! Surf's UP!!</h1>"
            f"<h2>Below is your Navigation Guide</h2>"
            f"<h3>/api/v1.0/precipitation  <-- Measuring the amount of rain and other weather conditions based on period of one year</h3>"
            f"<h3>/api/v1.0/stations    <-- Shows list of Stations ID and Names/Locations </h3>"
            f"<h3>/api/v1.0/tobs        <-- Display Tempatures and sort based on the most active station by descending order</h3>"
            f"<h3>/api/v1.0/<start><br/>"     f"<-- start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/></h3>"
            f"<h3>/api/v1.0/<start>/<end><br/>"  f"<-- displays start and the end date (YYYY-MM-DD), calculated the MIN/AVG/MAX temperature for dates between the start and end date inclusive</h3>"
            )
        
        
# Convert the query results from your precipitation analysis
# (i.e. retrieve only the last 12 months of data)
# to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp = session.query(Measurements.date, Measurements.prcp).\
    filter(Measurements.date >= last_year)
    session.close()
    prcp_list = dict(prcp)
    return jsonify(prcp_list)
    
    
#API Route to display list of all stations IDs and Names associated using List
@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(Station.station, Station.name)
    session.close()
    Stations = dict(station_query)
    return jsonify(Stations)


# Query the dates and temperature observations of
# the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    temp_results = session.query(Measurements.date, Measurements.tobs, Measurements.station).\
    filter(Measurements.date >= last_year).\
    group_by(Measurements.date).\
    order_by(func.count(Measurements.station)).all()
    temp = []
    for d, t, s in temp_results:
        row = {}
        row["date"] = d
        row["tobs"] = t
        row["station"] = s
        temp.append(row)
    session.close()
    return jsonify(temp)
    

'''
/api/v1.0/ and /api/v1.0//

Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

Hints*** Join the station and measurement tables for some of the queries. Use the Flask jsonify function to convert your API data to a valid JSON response object.

'''


@app.route("/api/v1.0/<start>")
def start_range(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date - last_year
    end =  dt.date(2017, 8, 23)
    start_query = session.query(Measurements.date, func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
    filter(Measurements.date >= date_start).\
    filter(Measurements.date <= date_end).all()
    dict_start = list(np.ravel(start_query))
    return jsonify(dict_start)
    
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start,  end):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    start_end_query = session.query(Measurements.date, func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
    filter(Measurements.date >= date_start).\
    filter(Measurements.date <= date_end).all()
    dict_start_end = list(np.ravel(start_end_query))
    return jsonify(dict_start_end)

if __name__ == '__main__':
    app.run(debug=True)
