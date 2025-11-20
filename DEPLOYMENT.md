# 법령 추적 시스템 - 클라우드 배포 가이드

## 개요

법령 추적 시스템을 Google Cloud Platform에 배포하는 방법을 안내합니다.

---

## 배포 옵션

### 1. Google Cloud Run (추천) 🚀
- **장점**: 자동 스케일링, 사용한 만큼 과금, 간단한 배포
- **비용**: 무료 티어 (월 200만 요청, 360,000 GB-초)
- **난이도**: ★☆☆☆☆

### 2. Google App Engine
- **장점**: 완전 관리형, 자동 스케일링
- **비용**: F1 인스턴스 무료 (하루 28시간)
- **난이도**: ★★☆☆☆

### 3. Google Compute Engine
- **장점**: 완전한 제어, 커스터마이징 가능
- **비용**: e2-micro 무료 티어 (특정 지역)
- **난이도**: ★★★★☆

---

## Option 1: Google Cloud Run 배포 (추천)

### 1.1 사전 준비

```bash
# Google Cloud SDK 설치 (macOS)
brew install google-cloud-sdk

# Google Cloud SDK 설치 (Linux)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Google Cloud SDK 설치 (Windows)
# https://cloud.google.com/sdk/docs/install 에서 다운로드

# 로그인
gcloud auth login

# 프로젝트 생성 및 설정
gcloud projects create law-tracking-system --name="법령 추적 시스템"
gcloud config set project law-tracking-system

# Cloud Run API 활성화
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 1.2 환경 변수 설정

```bash
# Secret Manager를 사용한 API 키 저장 (권장)
gcloud secrets create LAW_API_KEY --data-file=- <<< "psh@yi.ac.kr"

# 또는 .env 파일에 직접 포함 (비권장)
echo "LAW_API_KEY=psh@yi.ac.kr" > .env
```

### 1.3 배포 실행

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/Law-Tracking

# Cloud Run에 배포
gcloud run deploy law-tracking \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars LAW_API_KEY=psh@yi.ac.kr \
  --memory 512Mi \
  --cpu 1

# Secret Manager 사용 시
gcloud run deploy law-tracking \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-secrets LAW_API_KEY=LAW_API_KEY:latest \
  --memory 512Mi \
  --cpu 1
```

### 1.4 배포 확인

```bash
# 서비스 URL 확인
gcloud run services describe law-tracking --region asia-northeast3 --format 'value(status.url)'

# 브라우저에서 접속
# 출력된 URL (예: https://law-tracking-xxxxx.a.run.app) 접속
```

---

## Option 2: Google App Engine 배포

### 2.1 사전 준비

```bash
# App Engine 초기화
gcloud app create --region=asia-northeast3

# App Engine API 활성화
gcloud services enable appengine.googleapis.com
```

### 2.2 환경 변수 설정

`app.yaml` 파일에서 환경 변수 설정:

```yaml
env_variables:
  LAW_API_KEY: "psh@yi.ac.kr"
```

### 2.3 배포 실행

```bash
# App Engine에 배포
gcloud app deploy

# 배포 완료 후 브라우저에서 열기
gcloud app browse
```

---

## Option 3: Google Compute Engine 배포

### 3.1 VM 인스턴스 생성

```bash
# e2-micro 인스턴스 생성 (무료 티어)
gcloud compute instances create law-tracking-vm \
  --zone=asia-northeast3-a \
  --machine-type=e2-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=10GB \
  --tags=http-server,https-server

# 방화벽 규칙 추가
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --target-tags http-server

gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --target-tags https-server

gcloud compute firewall-rules create allow-flask \
  --allow tcp:5000 \
  --target-tags http-server
```

### 3.2 VM에 SSH 접속 및 설정

```bash
# SSH 접속
gcloud compute ssh law-tracking-vm --zone=asia-northeast3-a

# 서버에서 실행
sudo apt update
sudo apt install -y python3-pip python3-venv git

# 프로젝트 클론
git clone https://github.com/YOUR_USERNAME/Law-Tracking.git
cd Law-Tracking

# 가상 환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
echo "LAW_API_KEY=psh@yi.ac.kr" > .env

# Gunicorn으로 실행
gunicorn -b 0.0.0.0:5000 web_dashboard_adminlte:app &
```

### 3.3 systemd 서비스 설정 (자동 시작)

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/law-tracking.service
```

다음 내용 입력:

```ini
[Unit]
Description=Law Tracking System
After=network.target

[Service]
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Law-Tracking
Environment="PATH=/home/YOUR_USERNAME/Law-Tracking/venv/bin"
ExecStart=/home/YOUR_USERNAME/Law-Tracking/venv/bin/gunicorn -b 0.0.0.0:5000 web_dashboard_adminlte:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 활성화 및 시작
sudo systemctl enable law-tracking
sudo systemctl start law-tracking
sudo systemctl status law-tracking
```

---

## 배포 후 확인 사항

### 1. 서비스 상태 확인

```bash
# Cloud Run
gcloud run services describe law-tracking --region asia-northeast3

# App Engine
gcloud app versions list

# Compute Engine
gcloud compute instances list
```

### 2. 로그 확인

```bash
# Cloud Run
gcloud run logs read --service law-tracking --region asia-northeast3

# App Engine
gcloud app logs tail

# Compute Engine
gcloud compute ssh law-tracking-vm --zone=asia-northeast3-a
journalctl -u law-tracking -f
```

### 3. 메트릭 모니터링

- Google Cloud Console → 모니터링 → 대시보드
- CPU, 메모리, 요청 수, 응답 시간 확인

---

## 비용 최적화 팁

### 1. Cloud Run
- **무료 티어**: 월 200만 요청, 360,000 GB-초
- **최소 인스턴스 0 설정**: 사용하지 않을 때 비용 0원
- **타임아웃 설정**: 불필요한 장시간 요청 방지

### 2. App Engine
- **F1 인스턴스**: 하루 28시간 무료
- **자동 스케일링 설정**: min_instances=0

### 3. Compute Engine
- **e2-micro**: 특정 지역에서 무료 (미국 서부 등)
- **프리미티브 스팟 인스턴스**: 비용 80% 절감
- **자동 종료**: 사용하지 않을 때 VM 중지

---

## 도메인 연결

### 1. 커스텀 도메인 등록

```bash
# Cloud Run
gcloud run domain-mappings create --service law-tracking --domain law-tracking.example.com --region asia-northeast3

# App Engine
gcloud app domain-mappings create law-tracking.example.com
```

### 2. DNS 설정

- Google Domains, Cloudflare 등에서 CNAME 레코드 추가
- Cloud Run URL 또는 App Engine URL로 포인팅

---

## SSL/HTTPS 설정

- **Cloud Run**: 자동으로 HTTPS 제공
- **App Engine**: 자동으로 HTTPS 제공
- **Compute Engine**: Let's Encrypt 사용

```bash
# Compute Engine에서 Certbot 설치
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d law-tracking.example.com
```

---

## 백업 및 복구

### 1. 데이터 백업

```bash
# 로컬에서 데이터 다운로드
gcloud compute scp law-tracking-vm:/home/USER/Law-Tracking/data ./backup-data --zone=asia-northeast3-a --recurse

# Cloud Storage에 백업
gsutil -m cp -r data gs://law-tracking-backup/
```

### 2. 자동 백업 스크립트

```bash
# cron 설정
crontab -e

# 매일 자정에 백업
0 0 * * * cd /home/USER/Law-Tracking && tar -czf backup-$(date +\%Y\%m\%d).tar.gz data/
```

---

## 문제 해결

### 1. 502 Bad Gateway
- 메모리 부족: 인스턴스 메모리 증가
- 타임아웃: 요청 타임아웃 설정 확인

### 2. API 키 오류
- 환경 변수 확인: `echo $LAW_API_KEY`
- Secret Manager 권한 확인

### 3. 느린 응답
- 인스턴스 수 증가
- 캐싱 추가
- CDN 사용

---

## 참고 자료

- [Google Cloud Run 문서](https://cloud.google.com/run/docs)
- [Google App Engine 문서](https://cloud.google.com/appengine/docs)
- [Google Compute Engine 문서](https://cloud.google.com/compute/docs)
- [Flask 배포 가이드](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn 문서](https://docs.gunicorn.org/)

---

## 지원

문의사항이나 문제가 있으면 GitHub Issues에 등록해주세요.
