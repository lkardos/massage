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

@app.route("/offer")
def offer():
    massage_id = request.args.get("massage_id", None, type=int)
    
    try:
        massage = Massage.query.get(massage_id)
        if massage.name == '':
            raise AttributeError('Nobody owns massage %d, it can\'t be offered' % massage_id);
        massage.offered = True
        db.session.commit()
        
    except (TypeError, AttributeError) as e:
        return jsonify(status="error")
    return jsonify(status="ok")

@app.route("/take_form")
def take_form():
    massage_id = request.args.get("massage_id", None, type=int)
    massage = Massage.query.get(massage_id)
    if massage.name == '' or not massage.offered:
        return render_template("sombody_was_quicker.html")
    else: 
        return render_template("take_form.html", massage_id=massage.id, massage_from=massage.start.isoformat(), massage_to=massage.end.isoformat())

@app.route("/take_form_submit")
def take_form_submit():
    massage_id = request.args.get("massage_id", None, type=int)
    user_name = request.args.get("user_name", None, type=str)
    
    massage = Massage.query.get(massage_id)
    if massage.name == '' or not massage.offered:
        return render_template("sombody_was_quicker.html")
    massage.name = user_name
    massage.offered = False
    db.session.commit()
    return render_template("succeed.html")
        
@app.route("/take")
def take():
    massage_id = request.args.get("massage_id", None, type=int)
    user_name = request.args.get("user_name", None, type=str)
    
    try:
        massage = Massage.query.get(massage_id)
        if massage.name == '' or not massage.offered:
            raise AttributeError('Sorry somebody was quicker than you (massage  id: %s)' % massage_id);
        massage.name = user_name
        massage.offered = False
        db.session.commit()
        
    except (TypeError, AttributeError) as e:
        return jsonify(status="error")
    return jsonify(status="ok")

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
        
@app.route("/get_user")
def get_user():
    try:
        username = request.environ.get('REMOTE_USER')
    except (KeyError) as e:
        return jsonify(status = "error")

    return jsonify(username=request.environ.get('REMOTE_USER'), status="ok") #jsonify(username=user, status="ok")




if __name__ == "__main__":
    app.run()
