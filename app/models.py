from app import db 

class Sensor_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_number = db.Column(db.Integer(), index=True)
    time_stamp = db.Column(db.Float(), index=True)
    pressure = db.Column(db.Float(), index=True)
    proximity = db.Column(db.Float(), index=True)
    
    def __str__(self):
        return str(self.collection_number) + "," + str(self.time_stamp) + "," + str(self.pressure) + "," + str(self.temperature)


