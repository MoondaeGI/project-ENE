from typing import List, Optional
from sqlalchemy.orm import Session
from repositories import PersonRepository
from models.person import Person
from schemas.person import PersonCreate, PersonUpdate, PersonResponse
from utils.transactional import transactional
from config import get_db
from fastapi import Depends

class PersonService:
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.repo = PersonRepository(db)
    
    @transactional
    def create_person(self, person_data: PersonCreate) -> PersonResponse:
        person = Person(name=person_data.name)
        created_person = self.repo.create(person)
        self.db.refresh(created_person)

        return PersonResponse.model_validate(created_person)
    
    def get_person(self, person_id: int) -> Optional[PersonResponse]:
        person = self.repo.get(person_id)
        
        if not person:
            return None
        return PersonResponse.model_validate(person)
    
    def get_all_persons(self) -> List[PersonResponse]:
        persons = self.repo.get_all()

        return [PersonResponse.model_validate(person) for person in persons]
    
    @transactional
    def update_person(self, person_id: int, person_data: PersonUpdate) -> Optional[PersonResponse]:
        update_data = person_data.model_dump(exclude_unset=True)
        updated_person = self.repo.update(person_id, **update_data)

        if not updated_person:
            return None
        self.db.refresh(updated_person)

        return PersonResponse.model_validate(updated_person)
    
    @transactional
    def delete_person(self, person_id: int) -> bool:
        success = self.repo.delete(person_id)
        
        return success

