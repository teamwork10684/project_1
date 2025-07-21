from . import db

class SpeechRoomMember(db.Model):
    __tablename__ = 'speech_room_members'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('speech_rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp()) 