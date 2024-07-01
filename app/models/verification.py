from app.extensions import db
from datetime import datetime


class Verification(db.Model):
    __tablename__ = 'verifications'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(300), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    bvn = db.Column(db.String(11), nullable=False)
    date_verified = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # relationship
    user = db.relationship('User', backref=db.backref('verifications', lazy=True))

    def __repr__(self) -> str:
        return f'User>>> {self.user.email}'