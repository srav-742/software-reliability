from fastapi import APIRouter
from app.api.v1 import auth, health, projects, metrics, analyze, train, predict, explanation, models, history

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(metrics.router, tags=["metrics"])
api_router.include_router(analyze.router, tags=["analysis"])
api_router.include_router(train.router, tags=["training"])
api_router.include_router(predict.router, tags=["prediction"])
api_router.include_router(explanation.router, tags=["explainability"])
api_router.include_router(models.router, tags=["models"])
api_router.include_router(history.router, tags=["history"])
