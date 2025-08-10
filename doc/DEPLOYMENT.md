# 서버 배포 가이드

## 1. 개요

이 문서는 Backtesting API 서버를 프로덕션 환경에 배포하는 방법을 설명합니다. Docker를 사용하는 방법과 클라우드 서버에 직접 배포하는 두 가지 주요 시나리오를 다룹니다.

## 2. Docker를 이용한 배포 (권장)

Docker를 사용하면 필요한 모든 환경이 포함된 컨테이너를 통해 배포하므로, 가장 안정적이고 이식성이 높은 방법입니다.

### 2.1. Dockerfile 직접 사용

1.  **이미지 빌드**: 프로젝트 루트에서 Docker 이미지를 빌드합니다.
    ```bash
    docker build -t backtest-be-fast .
    ```
2.  **컨테이너 실행**: 빌드된 이미지를 백그라운드에서 실행합니다.
    ```bash
    docker run -p 8000:8000 -d --name backtest-server backtest-be-fast
    ```

### 2.2. Docker Compose 사용

`docker-compose.yml`을 사용하면 API 서버와 Nginx와 같은 다른 서비스를 함께 쉽게 관리할 수 있습니다.

```bash
# 프로젝트 루트에서 서비스를 빌드하고 백그라운드에서 실행
docker-compose up --build -d
```

---

## 3. 클라우드 서버 직접 배포 (Ubuntu 22.04 기준)

이 방법은 서버 환경을 직접 구성하고 관리해야 합니다.

### 3.1. 서버 초기 설정

1.  **인스턴스 준비**: 클라우드 제공업체(예: AWS EC2, Google Cloud)에서 Ubuntu 22.04 LTS 인스턴스를 생성합니다.
2.  **방화벽 설정**: SSH (22), HTTP (80), HTTPS (443) 포트를 엽니다. 보안을 위해 API 서버 포트(8000)는 외부에 직접 노출하지 않습니다.
3.  **기본 패키지 설치**:
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3-pip python3-venv nginx git -y
    ```

### 3.2. 애플리케이션 코드 배포

1.  **소스 코드 복제**:
    ```bash
    git clone <your-repo-url> /var/www/backtest_be_fast
    cd /var/www/backtest_be_fast
    ```
2.  **Python 환경 설정**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install gunicorn
    ```

### 3.3. 프로세스 관리자 설정 (systemd)

서버 부팅 시 애플리케이션이 자동으로 실행되고 안정적으로 동작하도록 systemd 서비스를 등록합니다.

1.  **서비스 파일 생성**:
    ```bash
    sudo nano /etc/systemd/system/backtest.service
    ```
2.  **서비스 파일 작성**:
    ```ini
    [Unit]
    Description=Backtest FastAPI Server
    After=network.target

    [Service]
    Type=simple
    User=ubuntu
    Group=www-data
    WorkingDirectory=/var/www/backtest_be_fast
    Environment="PATH=/var/www/backtest_be_fast/venv/bin"
    ExecStart=/var/www/backtest_be_fast/.venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
3.  **서비스 활성화 및 시작**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable backtest.service
    sudo systemctl start backtest.service
    ```

### 3.4. Nginx 리버스 프록시 설정

Nginx는 외부 요청을 받아 내부에서 실행 중인 FastAPI 애플리케이션(Gunicorn)으로 전달하는 리버스 프록시 역할을 합니다.

1.  **Nginx 설정 파일 생성**:
    ```bash
    sudo nano /etc/nginx/sites-available/backtest_be_fast
    ```
2.  **Nginx 설정 작성**:
    ```nginx
    server {
        listen 80;
        server_name your_domain.com; # 실제 도메인으로 변경

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```
3.  **설정 활성화**:
    ```bash
    sudo ln -s /etc/nginx/sites-available/backtest_be_fast /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```

### 3.5. HTTPS 설정 (Let's Encrypt)

Certbot을 사용하여 무료로 SSL 인증서를 발급받고 HTTPS를 적용합니다.

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com # 실제 도메인으로 변경
```

## 4. 배포 체크리스트

- [ ] `requirements.txt` 의존성 최종 확인
- [ ] `.env` 파일에 프로덕션용 환경 변수 설정 (DB 정보, 시크릿 키 등)
- [ ] Docker 이미지 빌드 및 실행 테스트 완료
- [ ] 클라우드 서버 방화벽 및 보안 그룹 규칙 설정 완료
- [ ] Nginx 리버스 프록시 설정 및 구문 검증 완료
- [ ] systemd 서비스를 통한 프로세스 자동 실행 및 재시작 설정 완료
- [ ] SSL 인증서 발급 및 HTTPS 리디렉션 설정 완료
- [ ] 서버 로그 로테이션 설정
- [ ] 시스템 및 애플리케이션 모니터링 설정
- [ ] 데이터베이스 및 중요 파일 백업 전략 수립