"""사용자 서비스"""
from typing import List, Optional
from schemas.person import PersonCreate, PersonUpdate, PersonResponse


class PersonService:
    _persons: List[dict] = []
    _next_id: int = 1
    

    @classmethod
    def create_person(cls, person_data: PersonCreate) -> PersonResponse:
        person_dict = {
            "id": cls._next_id,
            "name": person_data.name
        }
        cls._persons.append(person_dict)
        cls._next_id += 1
        return PersonResponse(**person_dict)
    

    @classmethod
    def get_person(cls, person_id: int) -> Optional[PersonResponse]:
        person = next((p for p in cls._persons if p["id"] == person_id), None)
        return PersonResponse(**person) if person else None
    

    @classmethod
    def get_all_persons(cls) -> List[PersonResponse]:
        return [PersonResponse(**person) for person in cls._persons]
    

    @classmethod
    def update_person(cls, person_id: int, person_data: PersonUpdate) -> Optional[PersonResponse]:
        person = next((p for p in cls._persons if p["id"] == person_id), None)
        if not person:
            return None
        
        update_data = person_data.model_dump(exclude_unset=True)
        person.update(update_data)
        return PersonResponse(**person)
    
    
    @classmethod
    def delete_person(cls, person_id: int) -> bool:
        person = next((p for p in cls._persons if p["id"] == person_id), None)
        if not person:
            return False
        
        cls._persons.remove(person)
        return True

