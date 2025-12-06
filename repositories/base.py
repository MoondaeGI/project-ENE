from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from config import Base
import traceback

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)

        try:
            self.db.flush()
            return obj
        except Exception as e:
            print("▶ flush error:", repr(e))
            traceback.print_exc()
            raise
    
    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        obj = self.get(id)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.flush()
        return obj
    
    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.flush()
        return True

