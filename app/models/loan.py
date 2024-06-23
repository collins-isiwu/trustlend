from app.extensions import db

class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 3), nullable=False)
    paid_off = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define a relationship to the User model
    user = db.relationship('User', back_populates='loans')
    
    def __repr__(self) -> str:
        return f"Loan> {self.amount}"