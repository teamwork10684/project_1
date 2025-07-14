from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()) 