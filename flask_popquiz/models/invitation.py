from . import db

class SpeechRoomInvitation(db.Model):
    __tablename__ = 'speech_room_invitations'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('speech_rooms.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role = db.Column(db.SmallInteger, nullable=False, default=0)
    status = db.Column(db.SmallInteger, nullable=False, default=0)
    invited_time = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp()) 