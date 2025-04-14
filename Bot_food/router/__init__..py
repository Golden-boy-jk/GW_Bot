from .CourierRequest import router as CourierRequest_router
from .CourierServiceRequest import router as CourierServiceRequest_router
from .RequestPass import router as RequestPass_router
from .MeetGuestRequest import router as MeetGuestRequest_router


routers = [
    RequestPass_router,
    CourierServiceRequest_router,
    CourierRequest_router,
    MeetGuestRequest_router,
]
