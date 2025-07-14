from . import db

class QuestionAnswer(db.Model):
    __tablename__ = 'question_answers'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('speech_rooms.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    selected_answer = db.Column(db.String(1))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp()) 