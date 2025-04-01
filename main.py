from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
import asyncio
import pandas as pd
import numpy as np
import warnings

app = FastAPI()


# 백테스트 전략 (이동평균 교차 전략) 정의
class SmaCross(Strategy):
    n1 = 10  # 단기 이동평균 기간
    n2 = 20  # 장기 이동평균 기간

    def init(self):
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Close)

    def next(self):
        if crossover(self.sma1, self.sma2):
            # 전체 자산의 일부만 사용하여 매수
            self.buy(size=0.5)  # 예: 가용 자금의 50%만 사용
        elif crossover(self.sma2, self.sma1):
            self.sell()

# 요청 파라미터 모델 정의
class BacktestRequest(BaseModel):
    symbol: str  # 예: "AAPL"
    start_date: str  # 예: "2020-01-01"
    end_date: str  # 예: "2021-01-01"
    cash: float = 10000
    commission: float = 0.002


# 재귀적 직렬화 함수
def recursive_serialize(obj):
    # 기본 JSON 직렬화 가능한 타입이면 그대로 반환
    if isinstance(obj, (str, int, bool)) or obj is None:
        return obj
    # Float 값 처리: inf, -inf, NaN 등을 문자열로 변환
    if isinstance(obj, float):
        if pd.isna(obj) or np.isnan(obj):
            return "NaN"
        if np.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        return obj
    # dict인 경우, 모든 값을 재귀적으로 직렬화
    if isinstance(obj, dict):
        return {k: recursive_serialize(v) for k, v in obj.items()}
    # list, tuple, set 인 경우 각각 순회
    if isinstance(obj, (list, tuple, set)):
        return [recursive_serialize(v) for v in obj]
    # Pandas DataFrame 은 dict로 변환 (리스트의 레코드 형태)
    if isinstance(obj, pd.DataFrame):
        return obj.reset_index(drop=True).to_dict(orient='records')
    # Pandas Series 은 리스트로 변환
    if isinstance(obj, pd.Series):
        return obj.tolist()
    # Pandas Index는 리스트로 변환
    if isinstance(obj, pd.Index):
        return list(obj)
    # datetime 또는 Timestamp 객체
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    # 위에 해당하지 않는 경우, str()로 변환 (예: DatetimeEngine 등)
    return str(obj)


# 백테스트 실행을 위한 비동기 엔드포인트
@app.post("/backtest/")
async def run_backtest(req: BacktestRequest):
    def run_bt():
        data = yf.download(req.symbol, start=req.start_date, end=req.end_date)
        if data.empty:
            raise ValueError("지정한 종목에 대한 데이터가 존재하지 않습니다.")
        # 데이터 컬럼이 MultiIndex인 경우 평탄화
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        # 필요한 열만 선택
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        bt = Backtest(data, SmaCross, cash=req.cash, commission=req.commission)

        # 경고 캡처를 위한 설정
        warning_messages = []

        def warning_handler(message, category, filename, lineno, file=None, line=None):
            warning_messages.append(str(message))

        # 경고 핸들러 설정
        original_handler = warnings.showwarning
        warnings.showwarning = warning_handler

        try:
            stats = bt.run()
            # stats를 dict로 변환 후 재귀적 직렬화 적용
            stats_dict = stats._asdict() if hasattr(stats, '_asdict') else dict(stats)
            result = recursive_serialize(stats_dict)
            # 경고 메시지 추가
            if warning_messages:
                result['warnings'] = warning_messages
            return result
        finally:
            # 원래 경고 핸들러로 복원
            warnings.showwarning = original_handler

    try:
        result = await asyncio.to_thread(run_bt)
        return result
    except Exception as e:
        # 오류 발생 시 에러 메시지와 함께 응답
        error_response = {"error": str(e), "type": type(e).__name__}
        raise HTTPException(status_code=500, detail=error_response)


# 서버 실행을 위한 기본 루트 엔드포인트
@app.get("/")
def read_root():
    return {"message": "백테스팅 API가 실행 중입니다. '/backtest/' 엔드포인트로 요청을 보내세요."}