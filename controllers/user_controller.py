"""사용자 컨트롤러"""
from typing import List
from fastapi import APIRouter, HTTPException, status
from services import UserService
from schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    return UserService.create_user(user_data)


@router.get("", response_model=List[UserResponse])
async def get_all_users():
    return UserService.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {user_id}를 찾을 수 없습니다."
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate):
    user = UserService.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {user_id}를 찾을 수 없습니다."
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    success = UserService.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID {user_id}를 찾을 수 없습니다."
        )
    return None

