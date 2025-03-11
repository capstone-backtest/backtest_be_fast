# strategies/sma_strategy.py
import backtrader as bt

class SmaCross(bt.Strategy):
    """
    이동평균선 교차 전략:
      - 단기(pfast)가 장기(pslow)를 상향 돌파하면 매수,
      - 하향 돌파하면 매도.
    """
    params = dict(
        pfast=10,
        pslow=30,
    )

    def __init__(self):
        sma_short = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.pfast)
        sma_long = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.pslow)
        self.crossover = bt.indicators.CrossOver(sma_short, sma_long)

    def next(self):
        if not self.position:
            if self.crossover[0] > 0:
                self.buy()
        else:
            if self.crossover < 0:
                self.sell()
