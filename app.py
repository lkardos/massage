from flask import Flask, jsonify, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import datetime, dateutil.parser

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

from models import *


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get_data")
def get_data():
    start = request.args.get("start", None)
    end = request.args.get("end", None)

    try:
        massages = map(lambda x: x.serialize, Massage.query.filter(
                    Massage.start >= dateutil.parser.parse(start),
                    Massage.end <= dateutil.parser.parse(end)))
    except (ValueError, AttributeError) as e:
        return jsonify(status = "error")
    
    return jsonify(massages=massages, status="ok")

@app.route("/get_data_timestamp")
def get_data_timestamp():
    start = float(request.args.get("start", None))
    end = float(request.args.get("end", None))

    try:
        massages = map(lambda x: x.serialize_timestamp, Massage.query.filter(
                    Massage.start >= datetime.datetime.utcfromtimestamp(start),
                    Massage.end <= datetime.datetime.utcfromtimestamp(end)))
    except (ValueError, AttributeError) as e:
        return jsonify(status = "error")
    
    
    return jsonify(massages=massages, status="ok")


@app.route("/set_data")
def set_data():
    massage_id = request.args.get("massage_id", None, type=int)
    user_name = request.args.get("user_name", None, type=str)
    
    try:
        massage = Massage.query.get(massage_id)
        massage.name = user_name
        db.session.commit()
    except (TypeError, AttributeError) as e:
        return jsonify(status="error")
    return jsonify(status="ok")
        




if __name__ == "__main__":
    app.run()
