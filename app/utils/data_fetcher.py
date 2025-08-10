"""
주식 데이터 수집 유틸리티
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Optional
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class DataFetcher:
    """주식 데이터 수집 클래스"""
    
    def __init__(self, cache_dir: str = "data_cache"):
        """
        Args:
            cache_dir: 데이터 캐시 디렉토리
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_stock_data(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
        use_cache: bool = True,
        cache_hours: int = 24
    ) -> pd.DataFrame:
        """
        주식 데이터를 가져옵니다.
        
        Args:
            ticker: 주식 티커 심볼
            start_date: 시작 날짜
            end_date: 종료 날짜
            use_cache: 캐시 사용 여부
            cache_hours: 캐시 유효 시간 (시간)
            
        Returns:
            OHLCV 데이터프레임
        """
        try:
            # 티커를 대문자로 변환
            ticker = ticker.upper()
            
            # 캐시 파일 경로
            cache_file = self.cache_dir / f"{ticker}_{start_date}_{end_date}.csv"
            
            # 캐시된 데이터 확인
            if use_cache and cache_file.exists():
                # 과거 데이터인지 확인 (종료일이 오늘 이전이면 과거 데이터)
                is_historical = end_date < date.today()
                
                if is_historical:
                    # 과거 데이터는 영구 캐시 (시간 체크 없음)
                    logger.info(f"과거 데이터 캐시 사용 (영구): {ticker}")
                    try:
                        data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                        if not data.empty and len(data) > 0:
                            return data
                    except Exception as e:
                        logger.warning(f"캐시 파일 읽기 실패, 새로 다운로드: {e}")
                else:
                    # 현재/미래 데이터만 시간 체크
                    file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if (datetime.now() - file_time).total_seconds() < cache_hours * 3600:
                        logger.info(f"최신 데이터 캐시 사용 ({cache_hours}시간 유효): {ticker}")
                        try:
                            data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                            if not data.empty and len(data) > 0:
                                return data
                        except Exception as e:
                            logger.warning(f"캐시 파일 읽기 실패, 새로 다운로드: {e}")
            
            # Yahoo Finance에서 데이터 다운로드
            logger.info(f"Yahoo Finance에서 데이터 다운로드: {ticker}")
            
            # 날짜를 문자열로 변환 (yfinance 호환성)
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = (end_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')  # 종료일 포함
            
            # yfinance 객체 생성
            stock = yf.Ticker(ticker)
            
            # 데이터 다운로드 시도
            data = None
            error_messages = []
            
            # 방법 1: stock.history() 사용
            try:
                data = stock.history(
                    start=start_str,
                    end=end_str,
                    auto_adjust=True,
                    prepost=False
                )
                if data is not None and not data.empty:
                    logger.info(f"stock.history()로 데이터 수집 성공: {ticker}")
            except Exception as e:
                error_messages.append(f"stock.history() 실패: {e}")
                logger.warning(f"stock.history() 실패: {e}")
            
            # 방법 2: yf.download() 사용 (첫 번째 방법이 실패한 경우)
            if data is None or data.empty:
                try:
                    data = yf.download(
                        ticker,
                        start=start_str,
                        end=end_str,
                        auto_adjust=True,
                        prepost=False,
                        progress=False
                    )
                    if data is not None and not data.empty:
                        logger.info(f"yf.download()로 데이터 수집 성공: {ticker}")
                except Exception as e:
                    error_messages.append(f"yf.download() 실패: {e}")
                    logger.warning(f"yf.download() 실패: {e}")
            
            # 데이터 검증
            if data is None or data.empty:
                error_msg = f"티커 '{ticker}'에 대한 데이터를 찾을 수 없습니다. 오류: {'; '.join(error_messages)}"
                raise ValueError(error_msg)
            
            # MultiIndex 컬럼 처리 (yfinance는 때때로 MultiIndex를 반환)
            logger.info(f"원본 컬럼 구조: {data.columns}, 타입: {type(data.columns)}")
            
            if isinstance(data.columns, pd.MultiIndex):
                # MultiIndex인 경우 첫 번째 레벨만 사용
                data.columns = data.columns.get_level_values(0)
                logger.info(f"MultiIndex 처리 후 컬럼: {data.columns}")
            
            # 컬럼 이름 정리 (공백 제거)
            data.columns = [str(col).replace(' ', '') for col in data.columns]
            logger.info(f"정리된 컬럼: {data.columns.tolist()}")
            
            # 필요한 컬럼 확인 및 선택
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            available_columns = data.columns.tolist()
            missing_columns = [col for col in required_columns if col not in available_columns]
            
            logger.info(f"필요한 컬럼: {required_columns}")
            logger.info(f"사용 가능한 컬럼: {available_columns}")
            logger.info(f"누락된 컬럼: {missing_columns}")
            
            if missing_columns:
                logger.warning(f"누락된 컬럼: {missing_columns}")
                # 누락된 컬럼이 있어도 최소한 Close가 있으면 진행
                if 'Close' not in available_columns:
                    raise ValueError(f"필수 컬럼 'Close'가 없습니다. 사용 가능한 컬럼: {available_columns}")
                
                # 누락된 컬럼을 Close 값으로 대체
                for col in missing_columns:
                    if col in ['Open', 'High', 'Low']:
                        data[col] = data['Close']
                        logger.info(f"컬럼 '{col}'을 Close 값으로 대체")
                    elif col == 'Volume':
                        data[col] = 0
                        logger.info(f"컬럼 '{col}'을 0으로 설정")
            
            # 컬럼 순서 맞추기
            data = data[required_columns]
            
            # NaN 값 및 무한대 값 처리
            data = data.replace([np.inf, -np.inf], np.nan)
            data = data.dropna()
            
            if data.empty:
                raise ValueError(f"유효한 데이터가 없습니다: {ticker}")
            
            # 날짜 범위 확인
            if len(data) < 5:
                logger.warning(f"데이터가 너무 적습니다: {ticker}, {len(data)} 레코드")
            
            # 캐시에 저장
            if use_cache:
                try:
                    data.to_csv(cache_file)
                    logger.info(f"데이터 캐시 저장: {cache_file}")
                except Exception as e:
                    logger.warning(f"캐시 저장 실패: {e}")
            
            logger.info(f"데이터 수집 완료: {ticker}, {len(data)} 레코드")
            return data
            
        except Exception as e:
            logger.error(f"데이터 수집 실패: {ticker}, {str(e)}")
            raise ValueError(f"데이터 수집 실패: {ticker} - {str(e)}")
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        티커 유효성 검증
        
        Args:
            ticker: 검증할 티커
            
        Returns:
            유효성 여부
        """
        try:
            ticker = ticker.upper()
            stock = yf.Ticker(ticker)
            
            # 기본 정보 조회 시도
            info = stock.info
            
            # 최소한의 유효성 확인
            if info and (
                'regularMarketPrice' in info or 
                'previousClose' in info or
                'currentPrice' in info or
                len(info) > 5  # 기본적인 정보가 있는지 확인
            ):
                return True
                
            # 정보가 부족하면 실제 데이터 조회 시도
            hist = stock.history(period="5d")
            return not hist.empty
            
        except Exception as e:
            logger.error(f"티커 검증 실패: {ticker}, {e}")
            return False
    
    def get_ticker_info(self, ticker: str) -> dict:
        """
        티커 정보 조회
        
        Args:
            ticker: 티커 심볼
            
        Returns:
            티커 정보 딕셔너리
        """
        try:
            ticker = ticker.upper()
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 기본 정보 추출
            result = {
                'symbol': ticker,
                'company_name': info.get('longName', info.get('shortName', ticker)),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', None),
                'current_price': info.get('regularMarketPrice', info.get('previousClose', None)),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown'),
                'country': info.get('country', 'Unknown')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"티커 정보 조회 실패: {ticker}, {str(e)}")
            return {
                'symbol': ticker, 
                'error': str(e),
                'company_name': ticker,
                'sector': 'Unknown',
                'industry': 'Unknown'
            }
    
    def clear_cache(self, ticker: Optional[str] = None):
        """
        캐시 삭제
        
        Args:
            ticker: 특정 티커의 캐시만 삭제 (None이면 전체 삭제)
        """
        try:
            if ticker:
                ticker = ticker.upper()
                pattern = f"{ticker}_*.csv"
                for file in self.cache_dir.glob(pattern):
                    file.unlink()
                    logger.info(f"캐시 삭제: {file}")
            else:
                for file in self.cache_dir.glob("*.csv"):
                    file.unlink()
                logger.info("전체 캐시 삭제 완료")
        except Exception as e:
            logger.error(f"캐시 삭제 실패: {e}")


# 글로벌 인스턴스
data_fetcher = DataFetcher() 