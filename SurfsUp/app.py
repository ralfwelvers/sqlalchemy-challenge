# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, func

from flask import Flask, jsonify
import json

# date format for query
format = '%Y-%m-%d'

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# home page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Hello. Welcome to Ralf's Hawaii weather API. Details on the routes are below.<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"The <b>precipitation</b> route returns the last 12 months of precipitation data:<br/><br/>"
        f"<a href=""/api/v1.0/precipitation"">precipitation</a><br/><br/>"
        f"The <b>stations</b> route returns the complete list of stations:<br/><br/>"
        f"<a href=""/api/v1.0/stations"">stations</a><br/><br/>"
        f"The temperature observations <b>(tobs)</b> route returns the dates and temperature observations of the most-active station for the previous year of data:<br/><br/>"
        f"<a href=""/api/v1.0/tobs"">tobs</a><br/>"
        f"<br/>"
        f"There is also a route where you can pass in a <b>start date</b> and retrieve the minimum temperature, the average temperature, and the maximum temperature from the provided start date \
        to the most recent date available.<br/>"
        f"Here's the path and format for this route:<br/><br/>"
        f"/api/v1.0/&lt;start&gt;<br/><br/>The start date should be in the following format: YYYY-MM-DD"
        f" Here's an example for this route:<br/><br/>"
        f"/api/v1.0/2016-08-08<br/><br/>"
        f"There is also a route where you can pass in a <b>start date</b> and an <b>end date</b> to retrieve the minimum temperature, the average temperature, and the maximum temperature from the provided start date \
        to provided end date.<br/>"
        f"Here's the path and format for this route:<br/><br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/><br/>The start date and end date should be in the following format: YYYY-MM-DD"
        f" Here's an example for this route:<br/><br/>"
        f"/api/v1.0/2014-08-08/2016-08-08<br/><br/>"
        f"<a href=""/api/v1.0/contact"">contact</a><br/>"
        
    )

# returns temperature data from a provided start date
@app.route("/api/v1.0/<start>")
def temp_startdate(start):

    df2 = pd.read_sql_query(
    "select measurement.tobs from \
    measurement where measurement.date >= '" + str(start) + "'"
    ,con=engine)

    data = {
        "minimum temperature" : df2['tobs'].min(axis=0),
        "average temperature" : df2['tobs'].mean(axis=0),
        "maximum temperature" : df2['tobs'].max(axis=0),
    }

    if df2.empty:
        return f"No data returned."
    else:
        return jsonify(data)

# returns temperature data from a provided start date and end date
@app.route("/api/v1.0/<start>/<end>")
def temp_startdate_enddate(start,end):

    df2 = pd.read_sql_query(
    "select measurement.tobs from \
    measurement where measurement.date between '" + str(start) + "' and '" + str(end) + "'"
    ,con=engine)

    data = {
        "minimum temperature" : df2['tobs'].min(axis=0),
        "average temperature" : df2['tobs'].mean(axis=0),
        "maximum temperature" : df2['tobs'].max(axis=0),
    }

    if df2.empty:
        return f"No data returned."
    else:
        return jsonify(data)


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Design a query to retrieve the last 12 months of precipitation data. 
    # Starting from the most recent data point in the database. 
    # Calculate the date one year from the last date in data set.
    # Perform a query to retrieve the data and precipitation scores
    # Save the query results as a Pandas DataFrame.
    df = pd.read_sql_query(
        session.query(measurement.date, measurement.prcp).filter(measurement.date >= 
        dt.datetime.strptime(session.query(measurement).order_by(measurement.date.desc()).first().date, format) - relativedelta(years = 1)).statement
        ,con=engine)
    
    prcp_dict = df.set_index('date').to_dict()['prcp']

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():

    # SQL query using groupby and count function
    query = sqlalchemy.select([
        measurement.station
    ]).distinct()
    
    # get all the records
    result = engine.execute(query).fetchall()
    
    return jsonify({'stations': [dict(row) for row in result]})


@app.route("/api/v1.0/tobs")
def tobs():

    # SQL query using groupby and count function
    query = sqlalchemy.select([
        measurement.station,
        sqlalchemy.func.count(measurement.station)
    ]).group_by(measurement.station).order_by(sqlalchemy.func.count(measurement.station).desc())
    
    # get all the records
    result = engine.execute(query).fetchall()
    
    station_high = result[0][0]

    query2 = " select measurement.date from \
    measurement order by measurement.date desc limit 1"

    print(query2)
    result2 = engine.execute(query2).fetchall()

    date_filter = dt.datetime.strptime(result2[0][0],format) - relativedelta(years = 1)

    query3 = "select measurement.date, measurement.tobs from \
    measurement where station = '" + station_high + "'" + " and measurement.date >= '" + str(date_filter) + "'"

    result3 = engine.execute(query3).fetchall()

    return jsonify({'date and tobs': [dict(row) for row in result3]})


@app.route("/api/v1.0/contact")
def contact():
    email = "ralf.welvers@gmail.com"

    return f"Questions? Comments? Complaints? Shoot an email to {email}."


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

# Close Session
session.close()