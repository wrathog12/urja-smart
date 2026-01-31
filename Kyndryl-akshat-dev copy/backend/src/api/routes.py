from fastapi import APIRouter
from api.endpoints.upload import router as upload_router
from api.endpoints.chat import router as chat_router
from api.endpoints.speech import router as speech_router

routes = APIRouter()

# Include endpoint routers
routes.include_router(upload_router)
routes.include_router(chat_router)
routes.include_router(speech_router)

@routes.get("/health-check")
def health_check():
    return {
        "status_code": 200,
        "message": "Healthy like a fresh virtualenv on a Monday morning",
    }