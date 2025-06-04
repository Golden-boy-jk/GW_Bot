from .CourierRequest import router as CourierRequest_router
from .CourierServiceRequest import router as CourierServiceRequest_router
from .RequestPass import router as RequestPass_router
from .MeetGuestRequest import router as MeetGuestRequest_router
from .stationery import router as stationery_router
from .issue import router as issue_router
from .admin import router as admin_router


routers = [
    admin_router,
    RequestPass_router,
    CourierServiceRequest_router,
    CourierRequest_router,
    MeetGuestRequest_router,
    stationery_router,
    issue_router,
]
