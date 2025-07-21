from . import db

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    question = db.Column(db.String(255))
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    answer = db.Column(db.String(1))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    created = db.Column(db.Boolean, nullable=False, default=False)
    published = db.Column(db.Boolean, nullable=False, default=False)