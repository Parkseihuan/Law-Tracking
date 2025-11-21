# Google Cloud Scheduler 자동 스케줄링 설정 가이드

이 가이드는 Google Cloud Run에 배포된 법령 추적 시스템에 자동 스케줄링을 추가하는 방법을 설명합니다.

## 개요

Cloud Scheduler를 사용하면 컴퓨터가 꺼져 있어도 정해진 시간에 자동으로 법령 변경사항을 체크하고 이메일 알림을 받을 수 있습니다.

**작동 원리:**
1. Cloud Scheduler가 정해진 시간에 Cloud Run 엔드포인트(`/api/scheduled-check`)를 호출
2. Flask 앱이 법령 변경사항을 자동 체크
3. 변경사항이 있으면 설정된 이메일로 자동 발송

## 사전 준비사항

1. ✅ Google Cloud Run에 애플리케이션 배포 완료 ([DEPLOYMENT.md](DEPLOYMENT.md) 참고)
2. ✅ Cloud Run 서비스 URL 확인 (예: `https://law-tracking-xxxxx-uc.a.run.app`)
3. ✅ Google Cloud SDK(`gcloud`) 설치 및 로그인

## 1단계: Cloud Scheduler API 활성화

```bash
# Cloud Scheduler API 활성화
gcloud services enable cloudscheduler.googleapis.com

# 현재 프로젝트 확인
gcloud config get-value project
```

## 2단계: 시스템 설정 페이지에서 스케줄 설정

웹 대시보드의 **시스템 설정** 페이지에서 다음을 설정합니다:

1. **스케줄 활성화**: 체크
2. **Cron 표현식**: 원하는 주기 선택 (예: `0 9 * * *` = 매일 오전 9시)
3. **시간대**: `Asia/Seoul` 선택
4. **저장** 버튼 클릭

![스케줄 설정](docs/images/schedule-settings.png)

## 3단계: 이메일 알림 설정 (선택사항)

변경사항을 이메일로 받으려면 **이메일 알림 설정**을 구성합니다:

### Gmail 사용 시

1. [Google 앱 비밀번호](https://myaccount.google.com/apppasswords) 생성
2. 시스템 설정 페이지에서 입력:
   - **SMTP 서버**: `smtp.gmail.com`
   - **SMTP 포트**: `587`
   - **SMTP 사용자명**: `your-email@gmail.com`
   - **SMTP 비밀번호**: 앱 비밀번호 (16자리)
   - **수신자 이메일**: 알림을 받을 이메일 주소
3. **연결 테스트** 버튼으로 확인
4. **이메일 설정 저장** 클릭

### Naver 사용 시

- **SMTP 서버**: `smtp.naver.com`
- **SMTP 포트**: `587`
- **SMTP 사용자명**: `your-id@naver.com`
- **SMTP 비밀번호**: 네이버 비밀번호

## 4단계: Cloud Scheduler Job 생성

### 방법 1: gcloud CLI 사용 (권장)

```bash
# 환경 변수 설정
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export SERVICE_NAME="law-tracking"
export SERVICE_URL="https://law-tracking-xxxxx-uc.a.run.app"

# Cloud Scheduler Job 생성
gcloud scheduler jobs create http law-tracking-scheduler \
    --location=$REGION \
    --schedule="0 9 * * *" \
    --time-zone="Asia/Seoul" \
    --uri="${SERVICE_URL}/api/scheduled-check" \
    --http-method=POST \
    --oidc-service-account-email="${PROJECT_ID}@appspot.gserviceaccount.com" \
    --oidc-token-audience="${SERVICE_URL}"
```

**Cron 표현식 예시:**
- `0 9 * * *` - 매일 오전 9시
- `0 */6 * * *` - 매 6시간마다
- `0 9,18 * * *` - 매일 오전 9시, 오후 6시
- `0 9 * * 1-5` - 평일 오전 9시

### 방법 2: Google Cloud Console 사용

1. [Cloud Scheduler Console](https://console.cloud.google.com/cloudscheduler) 접속
2. **일정 만들기** 클릭
3. 다음 정보 입력:
   - **이름**: `law-tracking-scheduler`
   - **지역**: `us-central1`
   - **빈도**: `0 9 * * *`
   - **시간대**: `Asia/Seoul`
4. **대상 구성**:
   - **대상 유형**: HTTP
   - **URL**: `https://your-cloud-run-url/api/scheduled-check`
   - **HTTP 메서드**: POST
5. **인증**:
   - **Auth 헤더**: OIDC 토큰
   - **서비스 계정**: `[PROJECT_ID]@appspot.gserviceaccount.com`

## 5단계: Scheduler Job 확인 및 테스트

### Job 목록 확인
```bash
gcloud scheduler jobs list --location=$REGION
```

### 수동 실행 (테스트)
```bash
gcloud scheduler jobs run law-tracking-scheduler --location=$REGION
```

### 실행 로그 확인
```bash
# Cloud Run 로그 확인
gcloud logs read --limit=50 --format=json \
    --filter="resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}"
```

## 6단계: 모니터링 및 관리

### Scheduler Job 수정

```bash
# Cron 표현식 변경 (예: 12시간마다)
gcloud scheduler jobs update http law-tracking-scheduler \
    --location=$REGION \
    --schedule="0 */12 * * *"

# 시간대 변경
gcloud scheduler jobs update http law-tracking-scheduler \
    --location=$REGION \
    --time-zone="America/New_York"
```

### Scheduler Job 일시 중지/재개

```bash
# 일시 중지
gcloud scheduler jobs pause law-tracking-scheduler --location=$REGION

# 재개
gcloud scheduler jobs resume law-tracking-scheduler --location=$REGION
```

### Scheduler Job 삭제

```bash
gcloud scheduler jobs delete law-tracking-scheduler --location=$REGION
```

## 7단계: Cloud Run 권한 설정 (중요)

Cloud Scheduler가 Cloud Run을 호출할 수 있도록 권한을 부여해야 합니다:

```bash
# Cloud Run Invoker 권한 부여
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --region=$REGION \
    --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
    --role="roles/run.invoker"
```

## 문제 해결

### 1. "Permission Denied" 오류

**원인**: Cloud Run 호출 권한 부족

**해결**:
```bash
gcloud run services add-iam-policy-binding law-tracking \
    --region=us-central1 \
    --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
    --role="roles/run.invoker"
```

### 2. "Service Unavailable" 오류

**원인**: Cloud Run 서비스가 중지되었거나 시작 중

**해결**:
- Cloud Run Console에서 서비스 상태 확인
- 최소 인스턴스를 0에서 1로 변경 (항상 실행)

```bash
gcloud run services update law-tracking \
    --region=us-central1 \
    --min-instances=1
```

⚠️ **주의**: 최소 인스턴스를 1로 설정하면 비용이 발생합니다.

### 3. 이메일 발송 실패

**원인**: SMTP 설정 오류

**해결**:
- 시스템 설정 페이지에서 "연결 테스트" 실행
- Gmail 앱 비밀번호 재생성
- SMTP 포트 확인 (587 또는 465)

### 4. 스케줄이 실행되지 않음

**확인사항**:
```bash
# Scheduler Job 상태 확인
gcloud scheduler jobs describe law-tracking-scheduler --location=us-central1

# 최근 실행 기록 확인
gcloud scheduler jobs describe law-tracking-scheduler --location=us-central1 \
    --format="value(status.lastAttemptTime, status.state)"
```

## 비용 최적화

### 1. 무료 할당량 활용

- **Cloud Scheduler**: 월 3개 Job까지 무료
- **Cloud Run**: 월 200만 요청까지 무료
- **Compute Time**: 월 360,000 vCPU-초, 180,000 GiB-초까지 무료

### 2. 최소 인스턴스 0으로 설정

```bash
gcloud run services update law-tracking \
    --region=us-central1 \
    --min-instances=0
```

요청이 없으면 인스턴스가 0으로 스케일다운되어 비용이 발생하지 않습니다.

### 3. 적절한 스케줄 설정

- 필요 이상으로 자주 체크하지 않기
- 법령 변경은 보통 하루 1~2회면 충분
- 권장: `0 9 * * *` (매일 오전 9시) 또는 `0 9,18 * * *` (오전 9시, 오후 6시)

## 설정 완료 확인

다음을 확인하여 모든 설정이 완료되었는지 점검하세요:

- [ ] Cloud Scheduler Job 생성 완료
- [ ] Cloud Run 호출 권한 설정 완료
- [ ] 시스템 설정 페이지에서 스케줄 활성화
- [ ] 이메일 알림 설정 및 테스트 완료
- [ ] 수동 실행 테스트 성공
- [ ] 첫 번째 자동 실행 확인

## 다음 단계

1. **대시보드 확인**: 정기적으로 법령 변경 이력 확인
2. **알림 모니터링**: 이메일이 정상적으로 수신되는지 확인
3. **로그 검토**: Cloud Run 로그에서 오류 확인

## 참고 문서

- [Google Cloud Scheduler 문서](https://cloud.google.com/scheduler/docs)
- [Cloud Run 인증](https://cloud.google.com/run/docs/authenticating/service-to-service)
- [Cron 표현식 생성기](https://crontab.guru/)
- [Gmail 앱 비밀번호 생성](https://support.google.com/accounts/answer/185833)

## 지원

문제가 발생하면:
1. Cloud Run 로그 확인
2. Cloud Scheduler 실행 이력 확인
3. 시스템 설정 페이지에서 "수동 체크" 버튼으로 직접 테스트
4. GitHub Issues에 문의

---

**축하합니다! 🎉**

이제 컴퓨터가 꺼져 있어도 Cloud에서 자동으로 법령 변경사항을 체크하고 이메일로 알림을 받을 수 있습니다.
