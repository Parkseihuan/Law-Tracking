# 법령 개정 추적 시스템

국가법령정보센터 Open API를 활용한 법령 개정사항 추적 및 알림 시스템

## 📋 프로젝트 개요

사립학교법, 고등교육법 등 주요 법령의 개정 사항을 자동으로 추적하고, 변경된 내용의 신구대조표를 제공하는 프로그램입니다.

## ✨ 주요 기능

### 1. 법령 모니터링
- 📌 특정 법령을 감시 대상으로 등록
- 🔍 주기적 자동 확인 (스케줄러)
- 🔔 변경 감지 시 알림
- 💾 변경 이력 자동 저장

### 2. 신구대조표 생성
- 📊 3가지 형식 지원:
  - 텍스트 형식 (.txt)
  - HTML 표준 형식 (.html)
  - 좌우 비교 형식 (.html)
- 🎨 한글 친화적 스타일
- 📥 다운로드 가능한 보고서

### 3. API 탐색 도구
- 🧪 국가법령정보센터 API 테스트
- 📡 여러 엔드포인트 자동 시도
- 🔑 다양한 API 키 파라미터 지원

## 🚀 빠른 시작

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 열어 법제처에서 발급받은 승인키를 입력합니다:

```bash
LAW_API_KEY=your_actual_api_key_here
```

⚠️ **중요:** "psh"가 실제 API 키인지 [공공데이터포털](https://www.data.go.kr)에서 재확인하세요.

### 3. 프로그램 실행

#### API 탐색
```bash
python law_api_explorer.py
```

#### 법령 모니터링
```bash
python law_monitor.py
```

#### 신구대조표 생성 (데모)
```bash
python comparison_generator.py
```

## 📁 프로젝트 구조

```
Law-Tracking/
├── .env                           # API 키 설정
├── .gitignore                     # Git 제외 파일
├── requirements.txt               # Python 의존성
│
├── law_api_explorer.py           # API 탐색 도구
├── law_monitor.py                 # 법령 모니터링 시스템
├── comparison_generator.py        # 신구대조표 생성기
├── simple_api_test.py            # 간단한 API 테스트
│
├── data/                          # 데이터 저장소
│   ├── watched_laws.json         # 감시 대상 법령
│   ├── cache/                    # API 응답 캐시
│   └── history/                  # 변경 이력
│
├── output/                        # 신구대조표 출력
│   ├── *.txt                     # 텍스트 형식
│   └── *.html                    # HTML 형식
│
├── README.md                      # 프로젝트 소개
├── USAGE_GUIDE.md                # 사용 가이드
└── API_ANALYSIS_AND_IDEAS.md     # API 분석 및 아이디어
```

## 🔧 주요 기능 상세

### 법령 모니터링 사용법

```python
from law_monitor import LawMonitor

# 모니터 생성
monitor = LawMonitor(api_key="your_key")

# 법령 추가
monitor.add_law("사립학교법")
monitor.add_law("고등교육법")

# 감시 목록 확인
monitor.list_watched_laws()

# 업데이트 확인
updates = monitor.check_updates()
```

### 신구대조표 생성 사용법

```python
from comparison_generator import LawComparisonGenerator

generator = LawComparisonGenerator()

# 3가지 형식으로 생성
generator.generate_text_comparison(old, new, "사립학교법")
generator.generate_html_comparison(old, new, "사립학교법")
generator.generate_side_by_side_comparison(old, new, "사립학교법")
```

## 📚 문서

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - 상세 사용 가이드
  - 환경 설정
  - 각 기능별 사용법
  - 자동화 설정 (cron, systemd)
  - 알림 설정 (이메일, Slack, 텔레그램)
  - 문제 해결

- **[API_ANALYSIS_AND_IDEAS.md](API_ANALYSIS_AND_IDEAS.md)** - API 분석 및 구현 아이디어
  - 국가법령정보센터 API 서비스 목록
  - 구현 아이디어 (4가지 핵심 기능)
  - 시스템 아키텍처
  - 단계별 구현 계획
  - 기술 스택 추천

## 🎯 구현된 기능

- ✅ API 탐색 및 테스트 도구
- ✅ 법령 검색 및 조회
- ✅ 법령 모니터링 시스템
- ✅ 변경 감지 및 이력 저장
- ✅ 신구대조표 생성 (3가지 형식)
- ✅ 한글 친화적 HTML 출력

## 🔄 향후 계획

- [ ] 웹 대시보드 구현
- [ ] 실시간 알림 시스템
- [ ] 법령 간 비교 기능
- [ ] AI 기반 변경 요약
- [ ] 모바일 앱

## 🔗 참고 자료

### 공식 문서
- [국가법령정보센터](https://www.law.go.kr)
- [Open API 가이드](https://open.law.go.kr/LSO/openApi/guideList.do)
- [공공데이터포털](https://www.data.go.kr/data/15000115/openapi.do)

### 기술 문서
- [Requests](https://requests.readthedocs.io/)
- [Python difflib](https://docs.python.org/3/library/difflib.html)
- [APScheduler](https://apscheduler.readthedocs.io/)

## ⚠️ 현재 이슈

### API 접근 제한
현재 서버 환경에서 법제처 API 접근이 403 에러로 차단되고 있습니다.

**권장 해결 방법:**
1. 로컬 PC 환경에서 테스트
2. 공공데이터포털에서 실제 API 키 형식 확인
3. 승인키가 "psh"가 맞는지 재확인 (일반적으로 30-40자 영숫자 조합)

## 💡 사용 예시

### 신구대조표 결과물

프로그램 실행 시 생성되는 신구대조표 예시:

```
output/
├── 사립학교법_신구대조_20251118_053258.txt    (1.5KB)
├── 사립학교법_신구대조_20251118_053258.html   (8.2KB)
└── 사립학교법_비교_20251118_053258.html       (5.1KB)
```

각 파일은 브라우저에서 바로 확인하거나 PDF로 변환 가능합니다.

## 🤝 기여

이슈와 개선 제안을 환영합니다!

## 📝 라이선스

MIT License

---

**개발 시작일:** 2025-01-18
**최종 업데이트:** 2025-01-18
