from . import db

class PublishedQuestion(db.Model):
    __tablename__ = 'published_questions'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('speech_rooms.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    time_limit = db.Column(db.Integer, nullable=False, default=60)
    status = db.Column(db.SmallInteger, nullable=False, default=0)  # 0-进行中，1-已结束
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp()) 