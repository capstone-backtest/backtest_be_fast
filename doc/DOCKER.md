# Docker 사용 가이드

## 1. 개요

이 문서는 Backtesting API 서버를 Docker 컨테이너 환경에서 빌드, 실행, 배포하는 방법을 설명합니다. Docker를 사용하면 로컬 개발 환경과 프로덕션 환경의 일관성을 유지할 수 있습니다.

## 2. 빠른 시작

### 2.1. Docker 단일 컨테이너 실행

1.  **이미지 빌드**
    프로젝트 루트 디렉터리에서 다음 명령어를 실행하여 Docker 이미지를 빌드합니다.
    ```bash
    docker build -t backtest-be-fast .
    ```

2.  **컨테이너 실행**
    빌드된 이미지를 사용하여 컨테이너를 실행합니다.
    ```bash
    docker run -p 8000:8000 -d --name backtest-server backtest-be-fast
    ```

3.  **실행 확인**
    API 서버가 정상적으로 실행되었는지 확인합니다.
    ```bash
    curl http://localhost:8000/health
    ```

### 2.2. Docker Compose 사용

`docker-compose.yml` 파일이 있는 프로젝트 루트에서 다음 명령어를 실행합니다.
```bash
# 모든 서비스 빌드 및 백그라운드 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f api

# 서비스 중지 및 컨테이너 삭제
docker-compose down
```

## 3. Docker 구성 파일

### 3.1. Dockerfile

프로덕션 환경에 최적화된 Dockerfile 예시입니다.

```dockerfile
# 1. Builder Stage
FROM python:3.11-slim as builder

WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# 2. Final Stage
FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Non-root user 생성
RUN addgroup --system app && adduser --system --group app

# 빌드된 wheel 파일 및 소스 코드 복사
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
COPY ./app ./app
COPY ./run_server.py .

# 의존성 설치
RUN pip install --no-cache /wheels/*

# 디렉터리 소유권 변경
RUN chown -R app:app /app

# Non-root user로 전환
USER app

EXPOSE 8000

CMD ["python", "run_server.py"]
```

### 3.2. docker-compose.yml

API 서버와 Nginx 리버스 프록시를 함께 실행하는 `docker-compose.yml` 예시입니다.

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: backtest-api-server
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./data_cache:/app/data_cache
    environment:
      - LOG_LEVEL=INFO
      - DEBUG=false
    restart: unless-stopped
    expose:
      - 8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: backtest-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  data_cache:
    driver: local
```

## 4. 개발 환경 설정

로컬 개발 시에는 소스 코드 변경 사항이 즉시 반영되도록 볼륨 마운트를 활용하는 것이 유용합니다.

### 4.1. 개발용 Docker Compose (`docker-compose.dev.yml`)

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile # 개발 환경에서도 동일 Dockerfile 사용 가능
    container_name: backtest-api-dev
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=DEBUG
      - DEBUG=true
    volumes:
      - ./app:/app/app # 소스 코드 변경 실시간 반영
      - ./data_cache:/app/data_cache
    restart: "no"
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 5. 보안 고려사항

### 5.1. Non-Root User 사용

Dockerfile에서 `USER app`과 같이 non-root 사용자로 컨테이너를 실행하여 보안을 강화합니다.

### 5.2. 네트워크 분리

`docker-compose.yml`에서 내부 네트워크와 외부 네트워크를 분리하여 API 서버가 외부에 직접 노출되지 않도록 설정할 수 있습니다.

```yaml
# docker-compose.yml
services:
  api:
    networks:
      - internal_net
    # ...

  nginx:
    networks:
      - internal_net
      - external_net
    # ...

networks:
  internal_net:
    internal: true
  external_net:
```

### 5.3. 시크릿 관리

API 키나 데이터베이스 암호와 같은 민감한 정보는 `.env` 파일이나 Docker Swarm/Kubernetes의 시크릿 관리 기능을 사용하여 컨테이너에 주입하는 것이 안전합니다.
```bash
# .env 파일 사용 예시
docker-compose --env-file .env.prod up -d
```