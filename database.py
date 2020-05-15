from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

from main import app

app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'
db = SQLAlchemy(app)


class UserItems(db.Model):         
    id = db.Column(db.Integer, primary_key=True)        # id of record
    user_id = db.Column(db.Integer, nullable=False)     # id of owner
    asset_id = db.Column(db.Integer, nullable=False)    # id of asset - key to StockData
    count = db.Column(db.Integer, default=1, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):     
        return '<item %r>' % self.symbol 

class StockData(db.Model):                          # data scrapped
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), nullable=False, unique=True)
    last_price       = db.Column(db.Float)
    change_rel       = db.Column(db.Float)
    change_absolute  = db.Column(db.Float)

    def __str__(self):
        return f'stock data item. symbol: {self.symbol}, id: {self.id}'


class User(UserMixin, db.Model):    # usermisin for injest flask login features
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80)) # length - mind password hashing method

    def __repr__(self):    
        return '<item %r>' % self.username #orig
