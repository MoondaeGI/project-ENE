from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from config import get_db
from services import PersonService
from schemas.person import PersonCreate, PersonUpdate, PersonResponse

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(person_data: PersonCreate, db: Session = Depends(get_db)):
    return PersonService.create_person(person_data, db)


@router.get("", response_model=List[PersonResponse])
async def get_all_persons(db: Session = Depends(get_db)):
    return PersonService.get_all_persons(db)


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    person = PersonService.get_person(person_id, db)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(person_id: int, person_data: PersonUpdate, db: Session = Depends(get_db)):
    person = PersonService.update_person(person_id, person_data, db)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    success = PersonService.delete_person(person_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return None

