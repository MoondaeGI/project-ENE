from typing import List, Optional
from sqlalchemy.orm import Session
from repositories import PersonRepository
from models.person import Person
from schemas.person import PersonCreate, PersonUpdate, PersonResponse


class PersonService:
    
    @staticmethod
    def create_person(person_data: PersonCreate, db: Session) -> PersonResponse:
        repo = PersonRepository(db)
        person = Person(name=person_data.name)
        created_person = repo.create(person)
        db.flush()  
        db.refresh(created_person)

        return PersonResponse.model_validate(created_person)
    
    @staticmethod
    def get_person(person_id: int, db: Session) -> Optional[PersonResponse]:
        repo = PersonRepository(db)
        person = repo.get(person_id)
        
        if not person:
            return None
        return PersonResponse.model_validate(person)
    
    @staticmethod
    def get_all_persons(db: Session) -> List[PersonResponse]:
        repo = PersonRepository(db)
        persons = repo.get_all()

        return [PersonResponse.model_validate(person) for person in persons]
    
    @staticmethod
    def update_person(person_id: int, person_data: PersonUpdate, db: Session) -> Optional[PersonResponse]:
        repo = PersonRepository(db)
        update_data = person_data.model_dump(exclude_unset=True)
        updated_person = repo.update(person_id, **update_data)

        if not updated_person:
            return None
        db.flush()  
        db.refresh(updated_person)

        return PersonResponse.model_validate(updated_person)
    
    @staticmethod
    def delete_person(person_id: int, db: Session) -> bool:
        repo = PersonRepository(db)
        success = repo.delete(person_id)
        
        return success

