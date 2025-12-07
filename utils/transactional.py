# transactional.py
from functools import wraps
from sqlalchemy.orm import Session

def transactional(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        db: Session = getattr(self, "db", None)
        if db is None:
            raise RuntimeError("transactional: self.db(Session)이 필요합니다.")

        try:
            result = func(self, *args, **kwargs)
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
    return wrapper
