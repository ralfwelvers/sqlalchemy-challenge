# Import the dependencies.
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import pandas as pd

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
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"<a href=""/api/v1.0/precipitation"">precipitation</a><br/>"
        f"<a href=""/api/v1.0/stations"">stations</a><br/>"
        f"<a href=""/api/v1.0/tobs"">tobs</a><br/>"
        f"<br/>"
        f"<a href=""/api/v1.0/contact"">contact</a><br/>"
        
    )


@app.route("/")
def index():
    return "Hello. Welcome to Ralf's Hawaii weather API. Details on the routes are below."


@app.route("/api/v1.0/precipitation")
def precipitation():

    # date format for query
    format = '%Y-%m-%d'

    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
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



    return f"pending."

@app.route("/api/v1.0/tobs")
def tobs():



    return f"pending."


@app.route("/api/v1.0/contact")
def contact():
    email = "ralf.welvers@gmail.com"

    return f"Questions? Comments? Complaints? Shoot an email to {email}."


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

# Close Session
session.close()