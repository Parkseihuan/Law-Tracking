# Google Cloud Run / Docker 배포용 Dockerfile

FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 데이터 디렉토리 생성
RUN mkdir -p data/history data/cache data/snapshots

# 포트 설정
ENV PORT=8080

# Gunicorn으로 실행
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 web_dashboard_adminlte:app
