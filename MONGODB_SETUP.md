# MongoDB Atlas 설정 가이드

## 개요
Law-Tracking 애플리케이션의 데이터를 영구적으로 저장하기 위해 MongoDB Atlas (무료 클라우드 데이터베이스)를 설정합니다.

## 1. MongoDB Atlas 계정 생성

1. https://www.mongodb.com/cloud/atlas/register 접속
2. 이메일로 가입 또는 Google 계정으로 로그인
3. 무료 플랜 선택

## 2. 클러스터 생성

1. "Create a Cluster" 클릭
2. **FREE** 티어 선택 (M0 Sandbox)
3. **Provider**: AWS 선택
4. **Region**: Seoul (ap-northeast-2) 또는 Singapore 선택
5. **Cluster Name**: `law-tracking-cluster` (또는 원하는 이름)
6. "Create Cluster" 클릭 (생성에 1-3분 소요)

## 3. 데이터베이스 사용자 생성

1. 왼쪽 메뉴에서 **Database Access** 클릭
2. "Add New Database User" 클릭
3. **Authentication Method**: Password 선택
4. **Username**: 원하는 사용자명 입력 (예: `lawtracker`)
5. **Password**: 강력한 비밀번호 생성 (저장해두세요!)
   - 또는 "Autogenerate Secure Password" 클릭
6. **Database User Privileges**: "Read and write to any database" 선택
7. "Add User" 클릭

## 4. 네트워크 접근 설정

1. 왼쪽 메뉴에서 **Network Access** 클릭
2. "Add IP Address" 클릭
3. **Allow Access from Anywhere** 클릭
   - IP Address: `0.0.0.0/0` (자동 입력됨)
   - 설명: "Allow from anywhere"
4. "Confirm" 클릭

> [!WARNING]
> 프로덕션 환경에서는 특정 IP만 허용하는 것이 좋지만, Render의 IP가 동적이므로 모든 IP를 허용해야 합니다.

## 5. 연결 문자열 얻기

1. 왼쪽 메뉴에서 **Database** 클릭
2. 클러스터에서 "Connect" 버튼 클릭
3. "Connect your application" 선택
4. **Driver**: Python, **Version**: 3.12 or later 선택
5. 연결 문자열 복사:
   ```
   mongodb+srv://username:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
6. `<password>`를 실제 비밀번호로 교체

## 6. Render에 환경 변수 추가

1. https://dashboard.render.com/ 접속
2. Law-Tracking 서비스 선택
3. 왼쪽 메뉴에서 **Environment** 클릭
4. "Add Environment Variable" 클릭
5. 다음 변수 추가:
   - **Key**: `MONGODB_URI`
   - **Value**: 위에서 복사한 연결 문자열 (비밀번호 교체 완료된 것)
6. "Save Changes" 클릭

## 7. 재배포

환경 변수를 추가하면 Render가 자동으로 재배포합니다. 로그에서 다음 메시지를 확인하세요:

```
✅ MongoDB connected successfully
✅ Using MongoDB for data storage
```

## 8. 연결 확인

배포 완료 후:
1. 애플리케이션 URL 접속
2. `/health` 엔드포인트 확인:
   ```
   https://your-app.onrender.com/health
   ```
3. 응답에서 `"mongodb_connected": true` 확인

## 9. 데이터 마이그레이션 (선택사항)

기존 로컬 데이터가 있다면:
1. 로컬에서 `.env` 파일에 MongoDB URI 추가
2. 애플리케이션 실행
3. 법령 업데이트 확인 실행 - 자동으로 MongoDB에 저장됨

## 문제 해결

### 연결 실패
- 비밀번호에 특수문자가 있다면 URL 인코딩 필요
- 네트워크 접근 설정 확인 (0.0.0.0/0 허용되어 있는지)
- 클러스터가 완전히 생성되었는지 확인 (1-3분 소요)

### "Authentication failed"
- 데이터베이스 사용자의 비밀번호 확인
- 연결 문자열의 `<password>` 부분이 실제 비밀번호로 교체되었는지 확인

## MongoDB Atlas 무료 플랜 제한

- **Storage**: 512MB
- **RAM**: Shared
- **Connections**: 최대 500개 동시 연결
- **Backup**: 자동 백업 없음 (수동 export 가능)

Law-Tracking 애플리케이션은 이 제한 내에서 충분히 작동합니다.

## 참고 자료

- [MongoDB Atlas 문서](https://docs.atlas.mongodb.com/)
- [Python MongoDB 드라이버 문서](https://pymongo.readthedocs.io/)
