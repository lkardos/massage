from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import datetime, dateutil.parser
import local_config

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = local_config.database #'sqlite:////tmp/test.db'
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
    user_name = get_user() #request.args.get("user_name", None, type=str)
    
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
    user_name = get_user()
    
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

@app.route("/add_slots", methods=['GET', 'POST'])
def add_slots():
    if request.method == 'GET':
        message = request.args.get("message", "", type=str)
        return render_template("add_slots.html", message=message)
    else:
        date_from = request.form["date_from"]
        date_to = request.form["date_to"]

        date_from = dateutil.parser.parse(date_from).date()
        date_to = dateutil.parser.parse(date_to).date()


        slots_from = request.form.getlist("slot_from")
        slots_to = request.form.getlist("slot_to")

        delta = datetime.timedelta(1)

        while date_from <= date_to:
            for slot_from, slot_to in zip(slots_from, slots_to):
                f = dateutil.parser.parse(slot_from).time()
                t = dateutil.parser.parse(slot_to).time()
                wf = datetime.datetime.combine(date_from, f)
                wt = datetime.datetime.combine(date_from, t)

                m = Massage()
                m.start = wf
                m.end = wt
                m.name = ''
                db.session.add(m)
                db.session.commit()

                
            date_from += delta

        return redirect(url_for("add_slots", message="Successfully added."))

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
def get_user_json():
    remote_user = get_user() #request.environ.get('REMOTE_USER')
    if not remote_user:
        return jsonify(status = "error")
    return jsonify(user=remote_user, status="ok") 

def get_user():
    try:
        remote_user = request.environ.get('REMOTE_USER')
    except (KeyError) as e:
        return None
    remote_user = remote_user.split("@")[0]
    return remote_user


if __name__ == "__main__":
    app.run()
