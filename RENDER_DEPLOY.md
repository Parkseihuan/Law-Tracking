# Render 배포 가이드

## 배포 단계

### 1. Render 대시보드 접속
https://dashboard.render.com/ 에 로그인하세요.

### 2. 새 Web Service 생성
1. "New +" 버튼 클릭
2. "Web Service" 선택
3. GitHub 저장소 연결: `Parkseihuan/Law-Tracking` 선택

### 3. 설정
다음 설정을 입력하세요:

- **Name**: `law-tracking` (또는 원하는 이름)
- **Region**: Seoul (또는 가까운 지역)
- **Branch**: `main`
- **Root Directory**: (비워두기)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn web_dashboard_adminlte:app`

### 4. 환경 변수 설정
"Environment" 섹션에서 다음 환경 변수를 추가하세요:

- **LAW_API_KEY**: 국가법령정보센터 API 키 입력

### 5. 배포
"Create Web Service" 버튼을 클릭하면 자동으로 배포가 시작됩니다.

## 배포 후 확인

배포가 완료되면 Render에서 제공하는 URL (예: `https://law-tracking.onrender.com`)로 접속하여 확인하세요.

## 주의사항

1. **무료 플랜 제한**: 
   - 15분 동안 요청이 없으면 자동으로 sleep 모드로 전환됩니다
   - 다시 접속하면 약 30초 정도 소요됩니다

2. **데이터 영속성**:
   - Render의 무료 플랜은 파일 시스템이 임시적입니다
   - 재배포 시 `data/` 폴더의 내용이 삭제될 수 있습니다
   - 중요한 데이터는 외부 데이터베이스나 스토리지 사용을 권장합니다

3. **API 키 보안**:
   - 환경 변수로 설정한 API 키는 안전하게 보관됩니다
   - `.env` 파일은 GitHub에 커밋하지 마세요 (이미 .gitignore에 포함됨)
