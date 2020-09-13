import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>" 
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()
    
    all_precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
              
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(measurement.date).order_by(measurement.date.desc())
    lastdate =results[0][0]
    lastdate_dt = dt.date(int(lastdate[0:4]), int(lastdate[5:7]), int(lastdate[8:10]) ) 
    date_1yr_ago = lastdate_dt-dt.timedelta(days=365)

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)


# >>> When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and \
# equal to the start date.

@app.route("/api/v1.0/<start>")
def temps_start(start):

    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).all()
    session.close()

    # Convert list of tuples into normal list
    all_temps = list(np.ravel(results))
    return jsonify(all_temps)


# >>> When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates \
# between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start,end):

    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    # Convert list of tuples into normal list
    all_temps_range = list(np.ravel(results))
    return jsonify(all_temps_range)



if __name__ == '__main__':
    app.run(debug=True)

