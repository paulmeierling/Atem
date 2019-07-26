from app import db 

class Pressure_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_number = db.Column(db.Integer(), index=True)
    time_stamp = db.Column(db.Float(), index=True)
    pressure = db.Column(db.Float(), index=True)
    temperature = db.Column(db.Float(), index=True)
    
    def __str__(self):
        return str(self.time_stamp) + "," + str(self.pressure) + "," + str(self.temperature)


