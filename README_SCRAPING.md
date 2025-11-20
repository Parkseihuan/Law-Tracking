# 법령 관계 크롤링 가이드

## 개요

국가법령정보센터(https://www.law.go.kr)에서 법령 체계도를 크롤링하여 실제 법령 간 관계를 수집합니다.

## 크롤링 시스템 구성

### 1. `law_hierarchy_scraper.py`
- 법령 체계도 웹 페이지 크롤링
- HTML 파싱하여 상위법령, 하위법령, 관련법령 추출
- `data/law_relationships.json`에 결과 저장

### 2. `law_hierarchy.py` (수정됨)
- 크롤링된 관계 데이터 우선 사용
- 하드코딩된 관계는 fallback으로 사용
- 두 데이터 소스를 병합하여 완전한 관계 그래프 생성

### 3. `update_law_relationships.py`
- 통합 스크립트
- 추적 중인 모든 법령의 관계를 일괄 크롤링
- 웹 대시보드에 자동 반영

## 사용 방법

### 1단계: 법령 추적 추가
```bash
python law_tracker.py
```

### 2단계: 법령 관계 크롤링
```bash
python update_law_relationships.py
```

### 3단계: 웹 대시보드에서 확인
```bash
python web_dashboard.py
```
브라우저에서 http://localhost:5000/hierarchy 접속

## 크롤링 데이터 구조

`data/law_relationships.json`:
```json
{
  "사립학교법": {
    "법령명": "사립학교법",
    "법령일련번호": "000273",
    "수집일시": "2025-01-15T10:30:00",
    "상위법령": [
      {
        "법령명": "교육기본법",
        "법령일련번호": "000456"
      }
    ],
    "하위법령": [
      {
        "법령명": "사립학교법 시행령",
        "법령일련번호": "001234"
      }
    ],
    "관련법령": [
      {
        "법령명": "고등교육법",
        "법령일련번호": "000789"
      }
    ]
  }
}
```

## 주의사항

### 웹사이트 접근 제한
국가법령정보센터는 크롤링 방지를 위해 다음 조치를 취할 수 있습니다:
- HTTP 403 Forbidden 응답
- Rate limiting (요청 횟수 제한)
- IP 차단

### 대응 방법
1. **요청 간 대기**: 각 요청 사이에 1초 지연 (현재 적용됨)
2. **브라우저 헤더**: User-Agent 등 브라우저 헤더 사용 (현재 적용됨)
3. **세션 유지**: requests.Session으로 쿠키 유지 (현재 적용됨)
4. **재시도 로직**: 실패 시 자동 재시도
5. **캐싱**: 최근 7일 이내 크롤링된 데이터는 재사용

### 차단 시 대안
웹사이트가 접근을 차단하는 경우:
- 하드코딩된 관계 데이터가 fallback으로 사용됨
- 수동으로 관계 데이터를 `data/law_relationships.json`에 추가 가능
- API를 통한 관계 데이터 조회 방법 검토 (현재 API에는 관계 정보 없음)

## 크롤링 스케줄링

자동 크롤링을 위해 cron 설정:
```bash
# 매주 월요일 오전 2시에 실행
0 2 * * 1 cd /path/to/Law-Tracking && python update_law_relationships.py
```

## 문제 해결

### 크롤링이 작동하지 않는 경우
1. 인터넷 연결 확인
2. 웹사이트 접근 가능 여부 확인: https://www.law.go.kr
3. 로그 확인: 403 에러 또는 타임아웃 메시지
4. BeautifulSoup4 설치 확인: `pip install -r requirements.txt`

### 관계가 제대로 추출되지 않는 경우
웹사이트 HTML 구조가 변경되었을 수 있습니다.
`law_hierarchy_scraper.py`의 `_parse_hierarchy_page()` 메서드를 업데이트해야 합니다.

## 참고 자료

- 국가법령정보센터 체계도: https://www.law.go.kr/LSW//lsStmdInfoP.do
- Open API 문서: https://www.law.go.kr/DRF/lawSearch.do
