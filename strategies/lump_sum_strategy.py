# strategies/lump_sum_strategy.py
import backtrader as bt

class LumpSumStrategy(bt.Strategy):
    """
    거치식 투자 전략:
      - 초기 투자금(investment)을 한 번에 매수하고, 이후 추가 매매 없음.
      - start() 메서드에서 첫날 종가에 매수하도록 하여, 실제 첫 거래일 시점에 투자하는 것과 유사하게 시뮬레이션.
    """
    params = (
        ('investment', 12000000),
    )

    def __init__(self):
        self.invested = False

    def start(self):
        """
        데이터의 첫 bar가 처리되기 직전 시점에 한 번만 호출.
        여기서 첫날 종가를 기준으로 매수.
        """
        if not self.invested:
            # 첫 번째 bar의 날짜와 종가 로그를 확인
            first_bar_date = self.datas[0].datetime.date(0)
            price = self.datas[0].close[0]
            print(f"[start()] Lump-sum 투자: {self.params.investment}원, 날짜={first_bar_date}, price={price:.2f}")

            size = self.params.investment / price
            self.buy(size=size)
            self.invested = True

    def next(self):
        # 이미 start()에서 매수했으므로 추가 매매 로직 없음
        pass
