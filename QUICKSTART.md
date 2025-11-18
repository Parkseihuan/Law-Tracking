# 법령 추적 시스템 - 빠른 시작 가이드

## ✅ API 작동 확인됨!

**API 키 `psh`가 정상 작동합니다!**

로컬 PC에서 실행 시:
- ✅ 법령 검색 (lawSearch.do) - 정상
- ✅ 법령 상세 조회 (lawService.do) - 정상
- ❌ 개정이유 조회 (RevsInfo.do) - 미제공
- ❌ 법령 연혁 조회 (HRCInfo.do) - 미제공

---

## 🚀 설치 및 실행

### 1. 프로젝트 다운로드

```bash
git clone https://github.com/Parkseihuan/Law-Tracking.git
cd Law-Tracking
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. .env 파일 생성

프로젝트 폴더에 `.env` 파일을 만들고 아래 내용 입력:

```
LAW_API_KEY=psh
```

**Windows (메모장):**
1. 메모장에서 `LAW_API_KEY=psh` 입력
2. "다른 이름으로 저장" → 파일명: `.env` → 형식: "모든 파일"

**Windows (명령 프롬프트):**
```cmd
echo LAW_API_KEY=psh > .env
```

**Mac/Linux:**
```bash
echo "LAW_API_KEY=psh" > .env
```

### 4. 프로그램 실행

```bash
# 새로운 법령 추적 시스템 (권장)
python law_tracker.py

# API 탐색 도구
python law_api_explorer.py

# 신구대조표 생성 데모
python comparison_generator.py
```

---

## 📊 주요 기능

### 1. 법령 추적 시스템 (`law_tracker.py`)

실제 작동하는 API만 사용하는 개선된 버전입니다.

#### 기본 사용법

```python
from law_tracker import LawTracker

# 추적기 생성
tracker = LawTracker(api_key="psh")

# 법령 추가
tracker.add_law("사립학교법")
tracker.add_law("고등교육법")

# 추적 목록 확인
tracker.list_tracked_laws()

# 변경사항 확인
updates = tracker.check_updates()
```

#### 주요 특징

- ✅ 공포일자 변경 자동 감지
- ✅ 법령 스냅샷 자동 저장
- ✅ 변경 이력 기록
- ✅ JSON 형식 데이터 저장

#### 저장되는 데이터

```
data/
├── tracked_laws.json          # 추적 중인 법령 정보
├── snapshots/                 # 법령 스냅샷
│   ├── 사립학교법_273349_20250118_123456.json
│   └── 고등교육법_273309_20250118_123456.json
└── history/                   # 변경 이력
    └── updates_20250118_123456.json
```

---

## 🎯 실전 활용 예시

### 예시 1: 교육 관련 법령 모니터링

```python
from law_tracker import LawTracker

tracker = LawTracker(api_key="psh")

# 교육 관련 법령 추가
tracker.add_law("사립학교법")
tracker.add_law("고등교육법")
tracker.add_law("초중등교육법")
tracker.add_law("교육기본법")
tracker.add_law("유아교육법")

# 현재 상태 확인
tracker.list_tracked_laws()
```

### 예시 2: 특정 법령 상세 정보 확인

```python
# 사립학교법 상세 정보
tracker.get_law_info("사립학교법")
```

출력 예시:
```
법령명: 사립학교법
공포일자: 20250814
공포번호: 21011
시행일자: 20260215
제개정구분: 일부개정
소관부처: 교육부
전화번호: 044-203-6956
```

### 예시 3: 자동 모니터링 (스케줄러)

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from law_tracker import LawTracker

def check_updates():
    tracker = LawTracker(api_key="psh")
    updates = tracker.check_updates()

    if updates:
        print(f"🔔 {len(updates)}개 법령 변경!")
        # 이메일/알림 발송

scheduler = BlockingScheduler()
scheduler.add_job(check_updates, 'cron', hour=9)  # 매일 오전 9시
scheduler.start()
```

---

## 📊 검색 결과 예시

### 사립학교법 검색 결과

```json
{
  "법령일련번호": "273349",
  "법령명한글": "사립학교법",
  "법령ID": "000888",
  "공포일자": "20250814",
  "공포번호": "21011",
  "제개정구분명": "일부개정",
  "소관부처명": "교육부",
  "시행일자": "20250919"
}
```

### 고등교육법 검색 결과

```json
{
  "법령일련번호": "273309",
  "법령명한글": "고등교육법",
  "법령ID": "000899",
  "공포일자": "20250814",
  "공포번호": "21007",
  "제개정구분명": "일부개정",
  "소관부처명": "교육부",
  "시행일자": "20251001"
}
```

---

## 🔄 변경 감지 방식

### 1. 공포일자 비교
- 이전 공포일자와 현재 공포일자 비교
- 다를 경우 → 법령 개정됨

### 2. 법령일련번호 확인
- 개정 시 새로운 법령일련번호 부여됨
- 예: 273349 → 273400 (가상의 예)

### 3. 스냅샷 저장
- 변경 감지 시 전체 법령 정보 저장
- 나중에 신구대조표 생성 가능

---

## 💡 활용 팁

### Tip 1: 정기 확인 설정

**Windows 작업 스케줄러:**
1. 작업 스케줄러 열기
2. 기본 작업 만들기
3. 프로그램: `python`
4. 인수: `C:\path\to\law_tracker.py`
5. 트리거: 매일 오전 9시

**Linux cron:**
```bash
# crontab -e
0 9 * * * cd /path/to/Law-Tracking && python law_tracker.py
```

### Tip 2: 변경 시 알림 받기

```python
import smtplib
from email.mime.text import MIMEText

def send_notification(updates):
    msg = MIMEText(f"{len(updates)}개 법령이 개정되었습니다.")
    msg['Subject'] = '법령 개정 알림'
    msg['From'] = 'psh@yi.ac.kr'
    msg['To'] = 'psh@yi.ac.kr'

    # 학교 SMTP 서버로 발송
    # (SMTP 서버 설정 필요)
```

### Tip 3: 신구대조표 자동 생성

```python
from law_tracker import LawTracker
from comparison_generator import LawComparisonGenerator

tracker = LawTracker(api_key="psh")
generator = LawComparisonGenerator()

updates = tracker.check_updates()

for update in updates:
    # 스냅샷 파일에서 이전/현재 버전 로드
    # 신구대조표 생성
    pass
```

---

## 📁 프로젝트 구조

```
Law-Tracking/
├── .env                        # API 키 (직접 생성 필요)
├── law_tracker.py             # ⭐ 법령 추적 시스템 (권장)
├── law_api_explorer.py        # API 탐색 도구
├── comparison_generator.py    # 신구대조표 생성기
├── data/
│   ├── tracked_laws.json     # 추적 법령 목록
│   ├── snapshots/            # 법령 스냅샷
│   └── history/              # 변경 이력
└── output/                    # 신구대조표 출력
```

---

## ❓ FAQ

### Q: API 키가 작동하지 않아요
**A:** `.env` 파일이 제대로 생성되었는지 확인하세요.
```bash
# 파일 확인
cat .env
# 출력: LAW_API_KEY=psh
```

### Q: 403 에러가 발생해요
**A:** 로컬 PC에서 실행하고 계신가요? 클라우드/서버 환경에서는 IP 제한이 있을 수 있습니다.

### Q: 개정이유를 확인하고 싶어요
**A:** 개정이유 API는 제공되지 않습니다. 법령 상세 정보에서 확인 가능한 정보만 활용할 수 있습니다.

### Q: 어떤 법령을 추적할 수 있나요?
**A:** 법제처에 등록된 모든 법령을 추적할 수 있습니다. 검색으로 먼저 확인해보세요.

---

## 🎓 다음 단계

1. **자동화 설정**
   - 매일 자동 확인
   - 변경 시 알림

2. **신구대조표 생성**
   - 스냅샷 비교
   - HTML/PDF 출력

3. **웹 대시보드** (향후)
   - 실시간 모니터링
   - 그래프 시각화

---

**작성일:** 2025-01-18
**테스트 환경:** Windows 10/11, Python 3.8+
