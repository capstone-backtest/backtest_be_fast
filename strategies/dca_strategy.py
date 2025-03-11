# strategies/dca_strategy.py
import backtrader as bt

class DollarCostAveragingStrategy(bt.Strategy):
    """
    적립식 투자 전략:
      - 매월 첫 거래일에 일정 금액(investment)만큼 주식을 매수
    """
    params = (
        ('investment', 1000000),
    )

    def __init__(self):
        self.last_investment_month = None

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        # 매월 첫 거래일이면 매수
        if self.last_investment_month != current_date.month:
            self.last_investment_month = current_date.month
            price = self.datas[0].close[0]
            size = self.params.investment / price
            self.buy(size=size)
