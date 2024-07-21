from app.extensions import db
from app.models import TokenBlacklist

def is_token_blacklisted(jti):
    result = db.session.query(TokenBlacklist.id).filter_by(jti=jti).scalar() is not None
    return result