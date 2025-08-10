"""
API v1 라우터 통합
"""
from fastapi import APIRouter
from .endpoints import backtest, strategies, optimize

api_router = APIRouter()

# 각 엔드포인트 라우터를 메인 API 라우터에 포함
api_router.include_router(
    backtest.router,
    prefix="/backtest",
    tags=["백테스팅"]
)

api_router.include_router(
    strategies.router,
    prefix="/strategies",
    tags=["전략 관리"]
)

api_router.include_router(
    optimize.router,
    prefix="/optimize",
    tags=["최적화"]
) 