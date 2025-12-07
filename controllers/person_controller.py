from typing import List
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from config import get_db
from services import PersonService
from schemas.person import PersonCreate, PersonUpdate, PersonResponse
from exceptions import NotFoundError

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(person_data: PersonCreate, service: PersonService = Depends(PersonService)):
    return service.create_person(person_data)


@router.get("", response_model=List[PersonResponse])
async def get_all_persons(service: PersonService = Depends(PersonService)):
    return service.get_all_persons()


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, service: PersonService = Depends(PersonService)):
    person = service.get_person(person_id)
    if not person:
        raise NotFoundError(
            message=f"사용자 ID {person_id}를 찾을 수 없습니다.",
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(person_id: int, person_data: PersonUpdate, service: PersonService = Depends(PersonService)):
    person = service.update_person(person_id, person_data)
    if not person:
        raise NotFoundError(
            message=f"사용자 ID {person_id}를 찾을 수 없습니다.",
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    success = PersonService(db).delete_person(person_id)
    if not success:
        raise NotFoundError(
            message=f"사용자 ID {person_id}를 찾을 수 없습니다.",
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return None

