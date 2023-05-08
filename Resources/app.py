# import dependencies 
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )
    
    
#/api/v1.0/precipitation
#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.  

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
# Query all 
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

  # Convert list of tuples into normal list
    all_prcp=[]
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)
#################################################

#/api/v1.0/stations
#Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
# Query all 
    results = session.query(Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    
    session.close()
    
    all_station=[]
    for id,station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict['elevation']=elevation
        all_station.append(station_dict)
    return jsonify(all_station)
#################################################

#/api/v1.0/tobs
#Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tempartureobs():
    
    session = Session(engine)
    
# Query most active
    active_station= session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).first()
    most_active_station = active_station[0] 
    
    session.close() 
    
    print(most_active_station)
    
    return jsonify(most_active_station)
#################################################

#/api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):

    session = Session(engine)
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)

@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    
    session = Session(engine)
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)
if __name__ == '__main__':
    app.run(debug=True)

