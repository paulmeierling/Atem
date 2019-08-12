from app import db 

class Actuation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.Date(), index=True)
    description  = db.Column(db.String(400), default="Run description")

    avg_inflow = db.Column(db.Float(), index=True)
    start_breath = db.Column(db.Float(), index=True)
    end_breath = db.Column(db.Float(), index=True)
    sensor_data = db.relationship('Sensor_data', backref='Actuation', lazy=True)

    def __str__(self):
        return str(description)

class Sensor_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actuation_id = db.Column(db.Integer, db.ForeignKey(Actuation.id))
    time_stamp = db.Column(db.Float(), index=True)
    pressure = db.Column(db.Float(), index=True)
    proximity = db.Column(db.Float(), index=True)
    
    def __str__(self):
        return str(self.actuation_id) + "," + str(self.time_stamp) + "," + str(self.pressure) + "," + str(self.proximity)


