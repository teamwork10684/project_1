from . import db

class SpeechRoom(db.Model):
    __tablename__ = 'speech_rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    speaker_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    speaker_invite_code = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.SmallInteger, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()) 