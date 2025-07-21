from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db

class RawText(db.Model):
    __tablename__ = 'raw_texts'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, nullable=False)
    file_id = db.Column(db.Integer, nullable=False)
    page = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_type = db.Column(db.Integer, nullable=False, default=0)  # 0-ppt, 1-pdf, 2-其它
    used_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 