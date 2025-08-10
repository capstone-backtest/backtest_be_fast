#!/usr/bin/env python3
"""
API 서버 테스트 스크립트
"""
import asyncio
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.strategy_service import strategy_service
from app.services.backtest_service import backtest_service
from app.models.requests import BacktestRequest, OptimizationRequest
from app.utils.data_fetcher import data_fetcher
from datetime import date


async def test_data_fetcher():
    """데이터 페처 테스트"""
    print("=== 데이터 페처 테스트 ===")
    
    try:
        # 테스트 데이터 수집
        data = data_fetcher.get_stock_data(
            ticker="AAPL",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        print(f"✅ 데이터 수집 성공: {len(data)} 레코드")
        print(f"컬럼: {data.columns.tolist()}")
        print(f"데이터 범위: {data.index[0]} ~ {data.index[-1]}")
        
        # 티커 정보 조회
        info = data_fetcher.get_ticker_info("AAPL")
        print(f"✅ 티커 정보: {info.get('company_name', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 데이터 페처 테스트 실패: {e}")


def test_strategy_service():
    """전략 서비스 테스트"""
    print("\n=== 전략 서비스 테스트 ===")
    
    try:
        # 전략 목록 조회
        strategies = strategy_service.get_all_strategies()
        print(f"✅ 사용 가능한 전략: {len(strategies)}개")
        for name, info in strategies.items():
            print(f"  - {name}: {info['description']}")
        
        # 특정 전략 정보 조회
        sma_info = strategy_service.get_strategy_info("sma_crossover")
        print(f"✅ SMA 전략 파라미터: {list(sma_info['parameters'].keys())}")
        
        # 파라미터 검증 테스트
        params = strategy_service.validate_strategy_params("sma_crossover", {
            "short_window": 10,
            "long_window": 20
        })
        print(f"✅ 파라미터 검증 성공: {params}")
        
    except Exception as e:
        print(f"❌ 전략 서비스 테스트 실패: {e}")


async def test_backtest_service():
    """백테스트 서비스 테스트"""
    print("\n=== 백테스트 서비스 테스트 ===")
    
    try:
        # 백테스트 요청 생성
        request = BacktestRequest(
            ticker="AAPL",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 6, 30),
            initial_cash=10000,
            strategy="sma_crossover",
            strategy_params={
                "short_window": 10,
                "long_window": 20
            }
        )
        
        # 백테스트 실행
        result = await backtest_service.run_backtest(request)
        print(f"✅ 백테스트 성공")
        print(f"  최종 자본: ${result.final_equity:,.2f}")
        print(f"  총 수익률: {result.total_return_pct:.2f}%")
        print(f"  샤프 비율: {result.sharpe_ratio:.3f}")
        print(f"  총 거래수: {result.total_trades}")
        
    except Exception as e:
        print(f"❌ 백테스트 서비스 테스트 실패: {e}")


async def test_optimization():
    """최적화 테스트"""
    print("\n=== 최적화 테스트 ===")
    
    try:
        # 최적화 요청 생성 (간단한 범위로 테스트)
        request = OptimizationRequest(
            ticker="AAPL",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 6, 30),
            initial_cash=10000,
            strategy="sma_crossover",
            param_ranges={
                "short_window": [5, 15],
                "long_window": [20, 30]
            },
            method="grid",
            max_tries=20  # 빠른 테스트를 위해 적은 수로 설정
        )
        
        # 최적화 실행
        result = await backtest_service.optimize_strategy(request)
        print(f"✅ 최적화 성공")
        print(f"  최적 파라미터: {result.best_params}")
        print(f"  최적 점수: {result.best_score:.3f}")
        print(f"  실행 시간: {result.execution_time_seconds:.2f}초")
        
    except Exception as e:
        print(f"❌ 최적화 테스트 실패: {e}")


async def main():
    """메인 테스트 함수"""
    print("🚀 Backtesting API 서버 테스트 시작\n")
    
    # 각 테스트 실행
    await test_data_fetcher()
    test_strategy_service()
    await test_backtest_service()
    await test_optimization()
    
    print("\n✨ 모든 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main()) 