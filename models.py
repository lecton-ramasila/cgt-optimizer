from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    portfolios = db.relationship('Portfolio', backref='owner', lazy=True)

class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), default='Ireland')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    positions = db.relationship('Position', backref='portfolio', lazy=True)

class Position(db.Model):
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100))
    platform = db.Column(db.String(50))
    asset_type = db.Column(db.String(20)) # Stock, RSU, ESPP
    currency = db.Column(db.String(10), default='USD')
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'’Ànullable=False)
    lots = db.relationship('Lot', backref='position', lazy=True)
 

class Lot(db.Model):
    __tablename__ = 'lots'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    cost_per_share = db.Column(db.Float, nullable=False)
    units = db.Column(db.Float, nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
