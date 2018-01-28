from flask import Flask, make_response, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../../windspeed-db/windspeed.db'
db = SQLAlchemy(app)

@app.route('/')
def welcome():
    return 'Windspeed!'

@app.route('/devices')
def devices():
    devices = WindSpeedEntry.query.group_by(WindSpeedEntry.device_id).order_by(WindSpeedEntry.timestamp.desc())
    return render_template('devices.html', devices=devices)
    
@app.route('/devices/<int:device_id>', methods=['POST', 'GET'])
def windupdate(device_id):
    if request.method == 'POST':
        device = WindSpeedDevice.query.filter_by(id=device_id).first()
        if device != None:
            if device.verify(request.form['password']):
                ws = WindSpeedEntry(device_id=device.id, value=int(request.form['value']), timestamp=datetime.now(), ip=str(request.remote_addr))
                app.logger.debug(repr(ws))
                db.session.add(ws)
                db.session.commit()
                return make_response('Added entry successfully', 201)
            else:
                return make_response('Forbidden', 403)
        else:
            return make_response('Not device_id not found', 404)
    else:
        values = WindSpeedEntry.query.filter_by(device_id=device_id).order_by(WindSpeedEntry.timestamp.desc())
        return render_template('values.html', values=values)

class WindSpeedDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    pw_hash = db.Column(db.String(128))
    entries = db.relationship('WindSpeedEntry', backref='device', lazy=True)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def verify(self, password):
        return check_password_hash(self.pw_hash, password)


class WindSpeedEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('wind_speed_device.id'), nullable=False)
    
    def __repr__(self):
        return '[%s] <%s (%s)> %i' % (self.timestamp, self.device_id, self.ip, self.value)
