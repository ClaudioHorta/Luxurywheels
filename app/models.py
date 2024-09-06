from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime



class Client(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return Client.query.get(int(user_id))

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    transmission = db.Column(db.String(50), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    daily_rate = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    number_of_people = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.Text)
    last_revision_date = db.Column(db.Date)
    next_revision_date = db.Column(db.Date)

    active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"Vehicle(id={self.id}, brand='{self.brand}', model='{self.model}', category='{self.category}')"


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    special_request = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)  # Added price field
    payment_method = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Booking {self.id} - {self.car_id} - {self.user_id}>'
    

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.name}', '{self.email}')"


