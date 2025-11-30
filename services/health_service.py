"""헬스 체크 서비스"""
from datetime import datetime
from schemas.health import HealthResponse


class HealthService:
    """헬스 체크 비즈니스 로직"""
    
    @staticmethod
    def check_health() -> HealthResponse:
        """서버 상태 확인"""
        return HealthResponse(
            status="healthy",
            message="서버가 정상적으로 작동 중입니다."
        )

