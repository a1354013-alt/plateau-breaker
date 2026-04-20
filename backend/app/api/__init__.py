from .analytics import report_router
from .analytics import router as analytics_router
from .health_records import router as health_records_router
from .profile import router as profile_router

__all__ = ["health_records_router", "analytics_router", "report_router", "profile_router"]
