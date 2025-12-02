"""사용자 서비스"""
from typing import List, Optional
from schemas.person import PersonCreate, PersonUpdate, PersonResponse


class PersonService:
    _persons: List[dict] = []
    _next_id: int = 1
    
    @classmethod
    def create_user(cls, user_data: UserCreate) -> UserResponse:
        """사용자 생성"""
        user_dict = {
            "id": cls._next_id,
            "name": user_data.name,
            "email": user_data.email,
            "age": user_data.age
        }
        cls._users.append(user_dict)
        cls._next_id += 1
        return UserResponse(**user_dict)
    
    @classmethod
    def get_user(cls, user_id: int) -> Optional[UserResponse]:
        """사용자 조회"""
        user = next((u for u in cls._users if u["id"] == user_id), None)
        return UserResponse(**user) if user else None
    
    @classmethod
    def get_all_users(cls) -> List[UserResponse]:
        """모든 사용자 조회"""
        return [UserResponse(**user) for user in cls._users]
    
    @classmethod
    def update_user(cls, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """사용자 업데이트"""
        user = next((u for u in cls._users if u["id"] == user_id), None)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        user.update(update_data)
        return UserResponse(**user)
    
    @classmethod
    def delete_user(cls, user_id: int) -> bool:
        """사용자 삭제"""
        user = next((u for u in cls._users if u["id"] == user_id), None)
        if not user:
            return False
        
        cls._users.remove(user)
        return True

