from database import db
from datetime import datetime
from flask_login import UserMixin ,login_manager 




class Users(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Currency(db.Model):
    __tablename__ = "currency"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    infos = db.relationship('CurrencyInfo', backref='currency', lazy='dynamic')

    def __repr__(self):
        return f"<Currency {self.name} ({self.symbol})>"

class CurrencyInfo(db.Model):

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey("currency.id"), nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    change_rate = db.Column(db.Float)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(50), default='www.tgju.org')

    def __repr__(self):
        return f"<CurrencyPrice {self.currency.name}: {self.price}>"
