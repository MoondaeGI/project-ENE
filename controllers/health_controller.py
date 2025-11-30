"""헬스 체크 컨트롤러"""
from fastapi import APIRouter
from services.health_service import HealthService
from schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """헬스 체크 엔드포인트"""
    return HealthService.check_health()

