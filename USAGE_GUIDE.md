# 법령 개정 추적 시스템 사용 가이드

## 🚀 시작하기

### 1. 환경 설정

#### 1.1 패키지 설치
```bash
pip install -r requirements.txt
```

#### 1.2 API 키 설정
`.env` 파일에 법제처에서 발급받은 승인키를 입력합니다:

```bash
LAW_API_KEY=your_actual_api_key_here
```

**중요:**
- 현재 승인키 "psh"가 실제 API 키인지 확인이 필요합니다
- 일반적으로 공공데이터포털의 API 키는 30자 이상의 긴 영숫자 문자열입니다
- 공공데이터포털(https://www.data.go.kr)에서 재확인하시기 바랍니다

---

## 📋 주요 기능

### 1. API 탐색 (law_api_explorer.py)

국가법령정보센터 API의 다양한 엔드포인트를 테스트합니다.

```bash
python law_api_explorer.py
```

**제공 기능:**
- 법령 검색
- 법령 상세 조회
- 개정이유 조회
- 법령 연혁 조회

---

### 2. 법령 모니터링 (law_monitor.py)

특정 법령들을 주기적으로 모니터링하여 개정 사항을 추적합니다.

```bash
python law_monitor.py
```

#### 2.1 감시 대상 법령 추가
```python
from law_monitor import LawMonitor

monitor = LawMonitor(api_key="your_api_key")

# 법령 추가
monitor.add_law("사립학교법")
monitor.add_law("고등교육법")
```

#### 2.2 감시 목록 확인
```python
monitor.list_watched_laws()
```

#### 2.3 업데이트 확인
```python
updates = monitor.check_updates()

if updates:
    for update in updates:
        print(f"변경됨: {update['law_name']}")
```

#### 2.4 데이터 저장 구조
```
data/
├── watched_laws.json          # 감시 대상 법령 목록
├── cache/                     # API 응답 캐시
└── history/                   # 법령 변경 이력
    ├── 사립학교법_20250118_143020.json
    └── 고등교육법_20250120_091500.json
```

---

### 3. 신구대조표 생성 (comparison_generator.py)

법령의 개정 전후를 비교하는 신구대조표를 생성합니다.

```bash
python comparison_generator.py
```

#### 3.1 기본 사용법
```python
from comparison_generator import LawComparisonGenerator

generator = LawComparisonGenerator()

old_content = "개정 전 법령 내용..."
new_content = "개정 후 법령 내용..."

# 텍스트 형식
generator.generate_text_comparison(old_content, new_content, "사립학교법")

# HTML 형식
generator.generate_html_comparison(old_content, new_content, "사립학교법")

# 좌우 비교 형식
generator.generate_side_by_side_comparison(old_content, new_content, "사립학교법")
```

#### 3.2 출력 형식

**1) 텍스트 형식 (.txt)**
- Unified diff 형식
- 터미널/텍스트 에디터에서 확인
- 버전 관리 시스템 호환

**2) HTML 표준 형식 (.html)**
- difflib의 기본 HTML 출력
- 브라우저에서 바로 확인
- 변경 사항 하이라이트

**3) 좌우 비교 형식 (.html)**
- 개정 전/후를 좌우로 배치
- 가독성이 가장 좋음
- 프레젠테이션용으로 적합

#### 3.3 출력 파일 위치
```
output/
├── 사립학교법_신구대조_20251118_143020.txt
├── 사립학교법_신구대조_20251118_143020.html
└── 사립학교법_비교_20251118_143020.html
```

---

## 🔄 자동화 설정

### 스케줄러로 주기적 모니터링

#### Option 1: cron (Linux/Mac)

```bash
# 매일 오전 9시에 실행
0 9 * * * cd /path/to/Law-Tracking && python law_monitor.py
```

#### Option 2: Python APScheduler

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from law_monitor import LawMonitor
import os

def check_law_updates():
    api_key = os.getenv('LAW_API_KEY')
    monitor = LawMonitor(api_key)
    updates = monitor.check_updates()

    if updates:
        # 알림 발송 로직
        send_notification(updates)

scheduler = BlockingScheduler()
# 매일 오전 9시 실행
scheduler.add_job(check_law_updates, 'cron', hour=9)
scheduler.start()
```

#### Option 3: systemd (Linux)

```ini
# /etc/systemd/system/law-monitor.service
[Unit]
Description=Law Update Monitor
After=network.target

[Service]
Type=oneshot
User=your_user
WorkingDirectory=/path/to/Law-Tracking
ExecStart=/usr/bin/python3 law_monitor.py

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/law-monitor.timer
[Unit]
Description=Run Law Monitor Daily

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

활성화:
```bash
sudo systemctl enable law-monitor.timer
sudo systemctl start law-monitor.timer
```

---

## 📧 알림 설정

### 이메일 알림 예시

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(updates):
    sender = "your_email@gmail.com"
    receiver = "recipient@example.com"
    password = "your_app_password"

    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = f"법령 개정 알림 - {len(updates)}건"

    body = "다음 법령이 개정되었습니다:\n\n"
    for update in updates:
        body += f"- {update['law_name']}\n"

    message.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(message)
```

### Slack 웹훅 알림 예시

```python
import requests
import json

def send_slack_notification(updates, webhook_url):
    message = {
        "text": f"🔔 법령 개정 알림 ({len(updates)}건)",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*다음 법령이 개정되었습니다:*"
                }
            }
        ]
    }

    for update in updates:
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"• *{update['law_name']}*\n  변경일시: {update['timestamp']}"
            }
        })

    requests.post(webhook_url, data=json.dumps(message),
                  headers={'Content-Type': 'application/json'})
```

### 텔레그램 봇 알림 예시

```python
import requests

def send_telegram_notification(updates, bot_token, chat_id):
    message = f"🔔 법령 개정 알림 ({len(updates)}건)\n\n"

    for update in updates:
        message += f"• {update['law_name']}\n"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(url, data=data)
```

---

## 🔧 고급 설정

### API 요청 캐싱

빈번한 API 호출을 줄이기 위해 캐싱 사용:

```python
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

class APICache:
    def __init__(self, cache_dir="data/cache", ttl_hours=6):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, url, params):
        key_str = f"{url}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, url, params):
        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)

            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time < self.ttl:
                return cached['data']

        return None

    def set(self, url, params, data):
        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': data
            }, f, ensure_ascii=False, indent=2)
```

---

## 📊 API 사용량 모니터링

```python
import json
from datetime import datetime
from pathlib import Path

class APIUsageTracker:
    def __init__(self, log_file="data/api_usage.json"):
        self.log_file = Path(log_file)
        self.usage = self._load_usage()

    def _load_usage(self):
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def track(self, endpoint, success=True):
        date = datetime.now().strftime("%Y-%m-%d")

        if date not in self.usage:
            self.usage[date] = {}

        if endpoint not in self.usage[date]:
            self.usage[date][endpoint] = {"success": 0, "failure": 0}

        if success:
            self.usage[date][endpoint]["success"] += 1
        else:
            self.usage[date][endpoint]["failure"] += 1

        self._save_usage()

    def _save_usage(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage, f, ensure_ascii=False, indent=2)

    def get_daily_stats(self, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.usage.get(date, {})
```

---

## ⚠️ 문제 해결

### Q1. API 호출이 403 에러로 실패합니다

**가능한 원인:**
1. API 키가 올바르지 않음
2. IP 주소 기반 접근 제한
3. API 승인이 완료되지 않음

**해결 방법:**
1. 공공데이터포털에서 API 키 재확인
2. 로컬 환경에서 테스트
3. 법제처에 문의하여 승인 상태 확인

### Q2. 법령 변경이 감지되지 않습니다

**확인 사항:**
1. API 응답이 정상적으로 수신되는지 확인
2. 해시 값 계산 로직 확인
3. 로그 파일 확인

### Q3. 한글이 깨져서 표시됩니다

**해결 방법:**
- UTF-8 인코딩 사용 확인
- HTML 파일의 charset 확인
- 브라우저 인코딩 설정 확인

---

## 📚 추가 리소스

### 공식 문서
- [국가법령정보센터](https://www.law.go.kr)
- [Open API 가이드](https://open.law.go.kr/LSO/openApi/guideList.do)
- [공공데이터포털](https://www.data.go.kr/data/15000115/openapi.do)

### 관련 라이브러리
- [Requests](https://requests.readthedocs.io/)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [difflib](https://docs.python.org/3/library/difflib.html)

---

## 🤝 기여 및 지원

문제가 발생하거나 개선 제안이 있으시면 이슈를 등록해주세요.

---

**최종 업데이트:** 2025-01-18
