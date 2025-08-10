# API 명세서

## 1. 기본 정보

- **Base URL**: `/`
- **API Version**: `v1`
- **API Prefix**: `/api/v1`

## 2. 시스템

### GET /health

시스템의 상태를 확인합니다.

- **Tags**: `시스템`
- **응답 (200 OK)**: `HealthResponse`
  ```json
  {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00",
    "version": "1.0.0"
  }
  ```

## 3. 전략 (Strategies)

### GET /api/v1/strategies/

사용 가능한 모든 투자 전략의 목록과 정보를 조회합니다.

- **Tags**: `전략`
- **응답 (200 OK)**: `StrategyListResponse`
  ```json
  {
    "strategies": [
      {
        "name": "sma_crossover",
        "description": "단순 이동평균 교차 전략",
        "parameters": {
          "short_window": {
            "type": "int",
            "default": 10,
            "min": 5,
            "max": 50,
            "description": "단기 이동평균 기간"
          },
          "long_window": {
            "type": "int",
            "default": 20,
            "min": 10,
            "max": 200,
            "description": "장기 이동평균 기간"
          }
        }
      }
    ],
    "total_count": 1
  }
  ```

## 4. 백테스팅 (Backtesting)

### POST /api/v1/backtest/run

지정한 조건으로 백테스트를 실행하고, 상세한 성과 분석 결과를 반환합니다.

- **Tags**: `백테스트`
- **요청 본문**: `BacktestRequest`
  ```json
  {
    "ticker": "AAPL",
    "start_date": "2022-01-01",
    "end_date": "2023-12-31",
    "initial_cash": 10000,
    "strategy": "sma_crossover",
    "strategy_params": {
      "short_window": 20,
      "long_window": 50
    },
    "commission": 0.001,
    "spread": 0.0
  }
  ```
- **응답 (200 OK)**: `BacktestResult`
  ```json
  {
    "ticker": "AAPL",
    "strategy": "sma_crossover",
    "start_date": "2022-01-01",
    "end_date": "2023-12-31",
    "duration_days": 730,
    "initial_cash": 10000,
    "final_equity": 12500.50,
    "total_return_pct": 25.00,
    "annualized_return_pct": 11.80,
    "buy_and_hold_return_pct": 15.50,
    "cagr_pct": 11.80,
    "volatility_pct": 22.5,
    "sharpe_ratio": 0.52,
    "sortino_ratio": 0.75,
    "calmar_ratio": 0.65,
    "max_drawdown_pct": -18.2,
    "avg_drawdown_pct": -4.5,
    "total_trades": 25,
    "win_rate_pct": 60.0,
    "profit_factor": 1.8,
    "avg_trade_pct": 1.0,
    "best_trade_pct": 10.5,
    "worst_trade_pct": -5.5,
    "alpha_pct": 1.2,
    "beta": 1.1,
    "kelly_criterion": 0.1,
    "sqn": 1.5,
    "execution_time_seconds": 1.23,
    "timestamp": "2024-01-15T12:00:00Z"
  }
  ```

### POST /api/v1/backtest/chart-data

백테스트 결과를 시각화하는 데 필요한 모든 데이터를 생성하여 반환합니다.

- **Tags**: `백테스트`
- **요청 본문**: `BacktestRequest` (위와 동일)
- **응답 (200 OK)**: `ChartDataResponse`
  ```json
  {
    "ticker": "AAPL",
    "strategy": "sma_crossover",
    "start_date": "2022-01-01",
    "end_date": "2023-12-31",
    "ohlc_data": [
      {
        "timestamp": "2022-01-03T00:00:00",
        "date": "2022-01-03",
        "open": 177.83,
        "high": 182.88,
        "low": 177.71,
        "close": 182.01,
        "volume": 104487900
      }
    ],
    "equity_data": [
      {
        "timestamp": "2022-01-03T00:00:00",
        "date": "2022-01-03",
        "equity": 10000,
        "return_pct": 0,
        "drawdown_pct": 0
      }
    ],
    "trade_markers": [
      {
        "timestamp": "2022-02-10T00:00:00",
        "date": "2022-02-10",
        "price": 172.19,
        "type": "entry",
        "side": "buy",
        "size": 58.07,
        "pnl_pct": null
      }
    ],
    "indicators": [
      {
        "name": "SMA_20",
        "type": "line",
        "color": "#ff7300",
        "data": [
          {
            "timestamp": "2022-01-31T00:00:00",
            "date": "2022-01-31",
            "value": 168.55
          }
        ]
      }
    ],
    "summary_stats": {
      "total_return_pct": 25.00,
      "sharpe_ratio": 0.52,
      "max_drawdown_pct": -18.2,
      "win_rate_pct": 60.0,
      "total_trades": 25
    }
  }
  ```

## 5. 최적화 (Optimization)

### POST /api/v1/optimize/run

전략의 파라미터를 최적화하여 최고의 성과를 내는 조합을 찾습니다.

- **Tags**: `최적화`
- **요청 본문**: `OptimizationRequest`
  ```json
  {
    "ticker": "NVDA",
    "start_date": "2022-01-01",
    "end_date": "2023-12-31",
    "initial_cash": 10000,
    "strategy": "rsi_strategy",
    "param_ranges": {
      "rsi_period": [10, 20],
      "rsi_upper": [70, 80],
      "rsi_lower": [20, 30]
    },
    "method": "grid",
    "maximize": "Sharpe Ratio",
    "max_tries": 200,
    "commission": 0.001
  }
  ```
- **응답 (200 OK)**: `OptimizationResult`
  ```json
  {
    "ticker": "NVDA",
    "strategy": "rsi_strategy",
    "method": "grid",
    "total_iterations": 121,
    "best_params": {
      "rsi_period": 14,
      "rsi_upper": 75,
      "rsi_lower": 25
    },
    "best_score": 0.88,
    "optimization_target": "Sharpe Ratio",
    "backtest_result": {
      "ticker": "NVDA",
      "strategy": "rsi_strategy",
      "start_date": "2022-01-01",
      "end_date": "2023-12-31",
      "duration_days": 730,
      "initial_cash": 10000,
      "final_equity": 18500,
      "total_return_pct": 85.00,
      "annualized_return_pct": 36.0,
      "buy_and_hold_return_pct": 95.0,
      "cagr_pct": 36.0,
      "volatility_pct": 40.0,
      "sharpe_ratio": 0.88,
      "sortino_ratio": 1.2,
      "calmar_ratio": 1.0,
      "max_drawdown_pct": -36.0,
      "avg_drawdown_pct": -8.0,
      "total_trades": 40,
      "win_rate_pct": 55.0,
      "profit_factor": 2.0,
      "avg_trade_pct": 2.1,
      "best_trade_pct": 20.0,
      "worst_trade_pct": -10.0,
      "alpha_pct": -2.0,
      "beta": 1.5,
      "kelly_criterion": 0.15,
      "sqn": 2.0,
      "execution_time_seconds": 10.5,
      "timestamp": "2024-01-15T13:00:00Z"
    },
    "execution_time_seconds": 120.5,
    "timestamp": "2024-01-15T13:02:00Z"
  }
  ```