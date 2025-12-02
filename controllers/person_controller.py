from typing import List
from fastapi import APIRouter, HTTPException, status
from services import PersonService
from schemas.person import PersonCreate, PersonUpdate, PersonResponse

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(person_data: PersonCreate):
    return PersonService.create_person(person_data)


@router.get("", response_model=List[PersonResponse])
async def get_all_persons():
    return PersonService.get_all_persons()


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int):
    person = PersonService.get_person(person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(person_id: int, person_data: PersonUpdate):
    person = PersonService.update_person(person_id, person_data)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(person_id: int):
    success = PersonService.delete_person(person_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {person_id}를 찾을 수 없습니다."
        )
    return None

