
# Student Name : Radhika Balasubramaniam
# Project Description : Build a flask api for Hawaii climate

#import project dependencies
import numpy as np
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#import datetime
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# add the default route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
         f"/api/v1.0/<start>/<end>"
    )

# add the route for precipitation
@app.route('/api/v1.0/percipitation')
def percipitation():
   
    # Start session
    session = Session(engine)

    # Query the database
    results = session.query(measurement.date, measurement.prcp).all()

    # close session
    session.close()
  
    # build the percipitation list
    prcpList = []
    for prcp in results:
        prcp_dict = {}
        prcp_dict['Date'] = prcp.date
        prcp_dict['Percipitation'] = prcp.prcp
        prcpList.append(prcp_dict)
    
    return jsonify(prcpList)

# add the route for stations
@app.route('/api/v1.0/stations')
def stations():
   
    #Start session
    session = Session(engine)

    # Query the database
    results = session.query(station.name).all()

    # close session
    session.close()
  
    #build all stations list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

# add the route for tobs
@app.route('/api/v1.0/tobs')
def tobs():
   
    # Start session
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database

    from dateutil.relativedelta import relativedelta
    result = session.query(func.max(measurement.date).label('MaxDate')).first() 

    maxDate = result[0]
    minDate = dt.datetime.strptime(maxDate, '%Y-%m-%d').date() - relativedelta(years=1)

    
    subResults = session.query(measurement.station, func.count(measurement.tobs).label("totalcount")).\
                group_by(measurement.station).\
                order_by(func.count(measurement.tobs).desc()).limit(1)

    #get the date and temperature values
    
    results = session.query(measurement.station, measurement.date, measurement.tobs).\
            filter(measurement.date.between(minDate, maxDate)).\
            filter(measurement.station == subResults[0].station)   

    # close session
    session.close()
  
   # build the temperature with date list
    tempList = []
    for temp in results:
        temp_dict = {}
        temp_dict['Station'] = temp.station
        temp_dict['Date'] = temp.date
        temp_dict['tobs'] = temp.tobs
        tempList.append(temp_dict)
    
       
    return jsonify(tempList)

@app.route('/api/v1.0/<start>')
def startTemp(start):

    try:
        date_obj = dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return(f"Incorrect date format, should be yyyy-mm-dd")

    # Start session
    session = Session(engine)

    #get the date and temperature values
    
    results = session.query(func.min(measurement.tobs).label("tMin"), func.avg(measurement.tobs).label("tAvg"), \
                func.max(measurement.tobs).label("tMax")).filter(measurement.date >= start) 

    # close session
    session.close()
  
   
    tempStatList = []
    for tempStat in results:
        tempStat_dict = {}
        tempStat_dict['tMin'] = tempStat.tMin
        tempStat_dict['tAvg'] = tempStat.tAvg
        tempStat_dict['tMax'] = tempStat.tMax
        tempStatList.append(tempStat_dict)
    
       
    return jsonify(tempStatList)

@app.route('/api/v1.0/<start>/<end>')
def startEndTemp(start, end):


    try:
        date_obj = dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return(f"Incorrect start date format, should be yyyy-mm-dd")
    
    try:
        date_obj = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return(f"Incorrect end date format, should be yyyy-mm-dd")

    # Start session
    session = Session(engine)

    #get the date and temperature values
    
    results = session.query(func.min(measurement.tobs).label("tMin"), func.avg(measurement.tobs).label("tAvg"), \
                func.max(measurement.tobs).label("tMax")).filter(measurement.date.between(start, end)) 

    # close session
    session.close()
  
   
    tempStatList = []
    for tempStat in results:
        tempStat_dict = {}
        tempStat_dict['tMin'] = tempStat.tMin
        tempStat_dict['tAvg'] = tempStat.tAvg
        tempStat_dict['tMax'] = tempStat.tMax
        tempStatList.append(tempStat_dict)
    
       
    return jsonify(tempStatList)

if __name__ == '__main__':
    app.run(debug=True)