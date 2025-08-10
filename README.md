# Backtesting API Server

## 1. 개요

이 프로젝트는 주식 투자 전략의 성과를 분석하고 최적화하기 위한 FastAPI 기반의 REST API 서버입니다. 사용자는 다양한 투자 전략을 정의하고, 과거 데이터를 기반으로 백테스팅을 실행하여 전략의 수익률, 변동성, 최대 손실 등 다양한 성과 지표를 확인할 수 있습니다.

또한, Grid Search와 같은 방법을 통해 전략의 최적 파라미터를 탐색하는 기능을 제공하여 전략 개발 및 검증 과정을 지원합니다.

## 2. 주요 기능

*   **전략 백테스팅**: 사용자가 정의한 투자 전략을 과거 주가 데이터에 적용하여 성과를 시뮬레이션합니다.
*   **상세한 성과 분석**: 총 수익률, 연평균 복리 수익률(CAGR), 샤프 비율, 최대 손실(MDD) 등 20가지 이상의 상세한 성과 지표를 제공합니다.
*   **파라미터 최적화**: 전략의 성능을 극대화하는 최적의 파라미터 조합을 탐색합니다.
*   **동적 전략 관리**: `strategies` 디렉터리에 새로운 전략 파일을 추가하여 동적으로 API에 등록하고 테스트할 수 있습니다.
*   **차트 데이터 제공**: Matplotlib 또는 웹 기반 차트 라이브러리(Recharts, ECharts 등)와 쉽게 연동할 수 있는 JSON 형식의 차트 데이터를 생성합니다.
*   **비동기 처리**: FastAPI를 기반으로 비동기 처리를 지원하여 여러 요청을 효율적으로 처리합니다.

## 3. 프로젝트 구조

```
backtest_be_fast/
├── app/                # FastAPI 서버 핵심 코드
│   ├── api/            # API 라우팅 (v1 포함)
│   ├── core/           # 설정, 예외 등 핵심 기능
│   ├── models/         # Pydantic 데이터 모델 (요청/응답)
│   ├── services/       # 핵심 비즈니스 로직
│   └── utils/          # 공통 유틸리티 함수
├── strategies/         # 커스텀 투자 전략 파일
├── data_cache/         # 주가 데이터 캐시 폴더
├── doc/                # 프로젝트 관련 문서
├── .venv/               # Python 가상환경
├── Dockerfile          # Docker 이미지 빌드 설정
├── docker-compose.yml  # Docker Compose 실행 설정
├── requirements.txt    # Python 의존성 목록
└── run_server.py       # 서버 실행 스크립트
```

## 4. 초기 설정

### 4.1. 요구사항

*   Python 3.11+
*   Git

### 4.2. 설치 및 실행

1.  **저장소 복제**
    ```bash
    git clone <repository-url>
    cd backtest_be_fast
    ```

2.  **가상환경 생성 및 활성화**
    ```bash
    # Windows에서는 'py' 런처 사용을 권장합니다.
    py -m venv .venv

    # 가상환경 활성화
    # Windows
    .venv\Scripts\activate
    # macOS / Linux
    source .venv/bin/activate
    ```

3.  **의존성 설치**
    ```bash
    # (권장) 'py' 런처를 사용하여 현재 가상환경의 pip를 명시적으로 실행합니다.
    py -m pip install -r requirements.txt
    ```

4.  **환경변수 설정 (선택사항)**
    `env.example` 파일을 복사하여 `.env` 파일을 생성합니다. 기본값으로도 실행 가능합니다.
    ```bash
    cp env.example .env
    ```

5.  **서버 실행**
    ```bash
    # Uvicorn을 사용하여 개발 서버 실행 (자동 리로드 지원)
    uvicorn app.main:app --reload

    # 또는 제공된 스크립트 사용
    python run_server.py
    ```

6.  **API 문서 확인**
    서버가 실행되면, 웹 브라우저에서 아래 주소로 접속하여 API 문서를 확인할 수 있습니다.
    *   **Swagger UI**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
    *   **ReDoc**: [http://127.0.0.1:8000/api/v1/redoc](http://127.0.0.1:8000/api/v1/redoc)

## 5. API 주요 엔드포인트

### 5.1. 백테스트 실행

*   `POST /api/v1/backtest/run`

    지정된 조건으로 백테스트를 실행하고 상세한 성과 지표를 반환합니다.

    **요청 본문 (Request Body):**
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
      "commission": 0.001
    }
    ```

### 5.2. 사용 가능한 전략 목록 조회

*   `GET /api/v1/strategies/`

    `strategies` 디렉터리에 정의된 모든 전략의 이름, 설명, 파라미터 정보를 조회합니다.

### 5.3. 파라미터 최적화 실행

*   `POST /api/v1/optimize/run`

    지정된 파라미터 범위 내에서 최고의 성과를 내는 조합을 탐색합니다.

    **요청 본문 (Request Body):**
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
      "maximize": "Sharpe Ratio"
    }
    ```

## 6. Docker 사용법

### 6.1. 이미지 빌드

```bash
docker build -t backtest-api .
```

### 6.2. 컨테이너 실행

```bash
docker run -p 8000:8000 -d --name backtest-server backtest-api
```

### 6.3. Docker Compose 사용

```bash
docker-compose up -d --build
```

## 7. 코드 품질 관리

*   **포맷팅**: `black`, `isort`
*   **타입 체크**: `mypy`

```bash
# 코드 포맷팅
black .
isort .

# 타입 검사
mypy .
```