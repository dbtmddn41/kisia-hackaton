from backend import db
from datetime import datetime

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    
class Parter(db.Model):
    partner_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('partner'))
    partner_name = db.Column(db.String(20), nullable=False)
    partner_past_message = db.Column(db.String(4000), nullable=True)
    partner_messge_embedding = db.Column(db.PickleType, nullable=True)
    partner_email = db.Column(db.String(50), unique=True, nullable=False)
    
class FishingMessages(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    messge = db.Column(db.String(4000))
    messge_embedding = db.Column(db.PickleType, nullable=True)
