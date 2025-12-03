from typing import Optional, List
from sqlalchemy.orm import Session
from models.person import Person
from repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    
    def __init__(self, db: Session):
        super().__init__(Person, db)
    

    def get_all(self) -> List[Person]:
        return self.db.query(Person).all()


    def create(self, person: Person) -> Person:
        return super().create(person)

