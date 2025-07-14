from . import db

class SpeechRoomOnline(db.Model):
    __tablename__ = 'speech_room_online'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('speech_rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.SmallInteger, nullable=False, default=2)  # 0-创建者，1-演讲者，2-听众 