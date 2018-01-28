from flask import Flask, make_response, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../tmpdata/windspeed.db'
db = SQLAlchemy(app)

@app.route('/')
def welcome():
    return 'Windspeed!'

@app.route('/devices')
def devices():
    devices = WindSpeedEntry.query.group_by(WindSpeedEntry.device_id).order_by(WindSpeedEntry.timestamp.desc())
    return render_template('devices.html', devices=devices)
    
@app.route('/devices/<string:device_id>', methods=['POST', 'GET'])
def windupdate(device_id):
    if request.method == 'POST':
        ws = WindSpeedEntry(device_id=device_id, value=int(request.form['value']), timestamp=datetime.now(), ip=str(request.remote_addr))
        print(repr(ws))
        db.session.add(ws)
        db.session.commit()
        return make_response('Added article successfully', 201)
    else:
        values = WindSpeedEntry.query.filter_by(device_id=device_id).order_by(WindSpeedEntry.timestamp.desc())
        return render_template('values.html', values=values)

class WindSpeedEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Unicode, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    ip = db.Column(db.Unicode, nullable=False)
    
    def __repr__(self):
        return '[%s] <%s (%s)> %i' % (self.timestamp, self.device_id, self.ip, self.value)
