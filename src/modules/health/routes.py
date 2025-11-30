from fastapi import APIRouter

from ...schemas import APIResponse
from .models import WelcomeData, HealthData, StatusData
from .controllers import get_welcome_info, get_health_status, get_system_status


# Create router for health-related endpoints
router = APIRouter(
    tags=["Health"],
    responses={
        500: {"description": "Internal server error"},
        503: {"description": "Service unavailable"}
    }
)


@router.get("/", 
            response_model=APIResponse[WelcomeData],
            summary="API Welcome",
            description="Get API welcome information and documentation links")
async def read_root() -> APIResponse:
    welcome_data = get_welcome_info()
    
    return APIResponse.success_response(
        message="Welcome to Tasker API",
        data=welcome_data.model_dump()
    )


@router.get("/health", 
            response_model=APIResponse[HealthData],
            summary="Health Check",
            description="Check service health status for monitoring systems")
async def health_check() -> APIResponse:
    health_data = get_health_status()
    
    return APIResponse.success_response(
        message="Service is healthy",
        data=health_data.model_dump()
    )


@router.get("/status",
            response_model=APIResponse[StatusData],
            summary="Detailed Status",
            description="Get comprehensive system status and environment information")
async def get_status() -> APIResponse:
    status_data = get_system_status()
    
    return APIResponse.success_response(
        message="System status retrieved successfully",
        data=status_data.model_dump()
    )

