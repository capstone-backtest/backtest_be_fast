# routers/backtest.py
from fastapi import APIRouter
import backtrader as bt
import yfinance as yf
import pandas as pd

# 전략 임포트
from strategies.sma_strategy import SmaCross
from strategies.dca_strategy import DollarCostAveragingStrategy
from strategies.lump_sum_strategy import LumpSumStrategy

router = APIRouter()

def get_data(ticker: str, from_date: str, to_date: str) -> bt.feeds.PandasData:
    """
    yfinance로 주가 데이터를 다운로드하고,
    Backtrader가 사용하기 편하도록 컬럼을 평탄화하여 PandasData로 변환.
    여기서 auto_adjust=False를 사용하여 '원시 종가'를 가져옵니다.
    """
    df = yf.download(
        ticker,
        start=from_date,
        end=to_date,
        auto_adjust=False  # 조정 종가 대신 원시 종가 사용
    )

    # 데이터 확인용 로그 (선택):
    # print(df.head())
    # print(df.tail())
    # print(df.shape)

    # 튜플 컬럼 처리 (e.g. ('Close','AAPL')) -> 'close'
    new_columns = []
    for col in df.columns:
        if isinstance(col, tuple):
            new_columns.append(col[0].lower())
        else:
            new_columns.append(str(col).lower())
    df.columns = new_columns

    data_feed = bt.feeds.PandasData(
        dataname=df,
        datetime=None,
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1  # 사용하지 않는 컬럼은 -1
    )
    return data_feed

def run_strategy(strategy_class, cash: float, ticker: str, from_date: str, to_date: str, **kwargs):
    """
    Cerebro에 전략을 추가하고 백테스트를 수행한 뒤,
    최종 가치(final_value), 이익(profit), 수익률(ROI)을 딕셔너리로 반환.
    """
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(cash)

    data = get_data(ticker, from_date, to_date)
    cerebro.adddata(data)

    cerebro.addstrategy(strategy_class, **kwargs)
    cerebro.run()

    final_value = cerebro.broker.getvalue()
    profit = final_value - cash
    roi_percentage = (profit / cash) * 100

    return {
        "final_value": round(final_value, 2),
        "profit": round(profit, 2),
        "roi(%)": round(roi_percentage, 2)
    }

@router.get("/compare")
def compare_strategies(
    ticker: str = "AAPL",
    from_date: str = "2022-01-01",
    to_date: str = "2023-01-01",
    initial_cash: float = 12000000
):
    """
    세 가지 전략(SMA Cross, DCA, Lump Sum)을 동일한 종목/기간/초기자금으로 돌려서 비교.
    예: /api/compare?ticker=AAPL&from_date=2022-01-01&to_date=2023-01-01&initial_cash=12000000
    """
    results = {}

    # 1) 이동평균선 교차 전략
    results["SMA Cross"] = run_strategy(
        SmaCross,
        initial_cash,
        ticker,
        from_date,
        to_date,
        pfast=10, pslow=30
    )

    # 2) 적립식 투자 전략
    results["Dollar Cost Averaging"] = run_strategy(
        DollarCostAveragingStrategy,
        initial_cash,
        ticker,
        from_date,
        to_date,
        investment=1000000
    )

    # 3) 거치식 투자 전략 (start()에서 첫날 매수 & 날짜 로그 추가)
    results["Lump Sum"] = run_strategy(
        LumpSumStrategy,
        initial_cash,
        ticker,
        from_date,
        to_date,
        investment=12000000
    )

    return results
