# Witple Backend API

FastAPI 기반의 백엔드 API 서버입니다1.

## 🚀 기술 스택

- **Framework**: FastAPI
- **Database**: PostgreSQL (로컬 Docker), AWS RDS PostgreSQL (프로덕션)
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Container**: Docker & Docker Compose
- **Cache**: Redis
- **CI/CD**: GitHub Actions
- **Kubernetes**: AWS EKS
- **Container Registry**: Amazon ECR

## 📁 프로젝트 구조

```
witple_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 애플리케이션
│   ├── config.py            # 환경 설정
│   ├── database.py          # 데이터베이스 연결
│   ├── api/                 # API 라우터
│   │   ├── __init__.py
│   │   ├── auth.py          # 인증 API
│   │   ├── users.py         # 사용자 API
│   │   └── health.py        # 헬스체크 API
│   ├── models/              # 데이터베이스 모델
│   │   ├── __init__.py
│   │   ├── base.py          # 기본 모델
│   │   └── user.py          # 사용자 모델
│   ├── schemas/             # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── auth.py          # 인증 스키마
│   │   └── user.py          # 사용자 스키마
│   └── utils/               # 유틸리티 함수
│       ├── __init__.py
│       ├── auth.py          # 인증 유틸리티
│       └── security.py      # 보안 유틸리티
├── k8s/                     # Kubernetes 매니페스트
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── deployment-dev.yaml
│   └── service-dev.yaml
├── .github/workflows/       # GitHub Actions
│   ├── deploy.yml           # 프로덕션 배포
│   └── develop.yml          # 개발 환경 배포
├── alembic/                 # 데이터베이스 마이그레이션
├── Dockerfile               # Docker 이미지 설정
├── docker-compose.yml       # 개발 환경 Docker Compose
├── docker-compose.prod.yml  # 프로덕션 환경 Docker Compose
├── requirements.txt         # Python 의존성
├── alembic.ini             # Alembic 설정
├── env.example             # 환경 변수 예제
├── AWS_DEPLOYMENT.md       # AWS EC2 배포 가이드
├── EKS_DEPLOYMENT.md       # EKS CI/CD 배포 가이드
└── README.md               # 프로젝트 문서
```

## 🛠️ 설치 및 실행

### 1. 환경 설정

```bash
# 환경 변수 파일 복사
cp env.example .env

# 환경 변수 수정 (필요시)
nano .env
```

### 2. Docker로 실행 (권장)

#### 개발 환경
```bash
# 개발 환경 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

#### 프로덕션 환경
```bash
# 프로덕션 환경 실행
docker-compose -f docker-compose.prod.yml up --build
```

### 3. 로컬 실행

```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 인증 API

### 회원가입
```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "홍길동"
}
```

### 로그인
```bash
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "password123"
}
```

### 사용자 정보 조회
```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

## 🗄️ 데이터베이스

### 로컬 개발 환경
- **PostgreSQL**: Docker 컨테이너로 실행
- 자동으로 테이블 생성됨

### AWS 프로덕션 환경
- **AWS RDS PostgreSQL**: 클라우드 데이터베이스
- 고가용성 및 백업 지원

### 마이그레이션 (선택사항)
```bash
# Alembic 초기화 (처음 한 번만)
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 실행
alembic upgrade head
```

## 🔧 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `ENVIRONMENT` | 실행 환경 | `development` |
| `DATABASE_URL` | 데이터베이스 URL | `postgresql://witple_user:witple_password@localhost:5432/witple` |
| `REDIS_URL` | Redis URL | `redis://localhost:6379` |
| `SECRET_KEY` | JWT 시크릿 키 | `your-secret-key-change-in-production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 시간 | `30` |
| `ALLOWED_ORIGINS` | CORS 허용 도메인 | `http://localhost:3000` |

## 🐳 Docker 명령어

```bash
# 컨테이너 빌드
docker-compose build

# 컨테이너 실행
docker-compose up

# 백그라운드 실행
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 로그 확인
docker-compose logs -f backend

# 컨테이너 재시작
docker-compose restart backend
```

## 🚀 CI/CD 파이프라인

### GitHub Actions 워크플로우

#### 개발 환경 배포
```bash
# develop 브랜치에 푸시하면 자동 배포
git push origin develop
```

#### 프로덕션 환경 배포
```bash
# main 브랜치에 푸시하면 자동 배포
git push origin main
```

### 배포 환경

#### 개발 환경 (develop 브랜치)
- **네임스페이스**: `witple-dev`
- **리플리카**: 1개
- **리소스**: 최소 (비용 절약)

#### 프로덕션 환경 (main 브랜치)
- **네임스페이스**: `witple`
- **리플리카**: 3개 (HPA로 자동 스케일링)
- **리소스**: 충분한 리소스 할당

## 🧪 테스트

```bash
# 헬스체크
curl http://localhost:8000/api/v1/health

# 버전 확인
curl http://localhost:8000/api/v1/version
```

## 📝 주요 기능

- ✅ JWT 기반 인증
- ✅ 사용자 관리 (회원가입, 로그인, 프로필)
- ✅ CORS 설정
- ✅ 데이터베이스 연동
- ✅ Docker 컨테이너화
- ✅ 환경별 설정 분리
- ✅ API 문서 자동 생성
- ✅ GitHub Actions CI/CD
- ✅ AWS EKS 자동 배포
- ✅ 자동 스케일링 (HPA)
- ✅ 로드 밸런싱 (ALB)

## 🔄 프론트엔드 연결

프론트엔드에서 다음 설정으로 연결:

```javascript
// API 기본 URL
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 요청 예시
fetch(`${API_BASE_URL}/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password123'
  })
});
```

## 🚀 배포

### 로컬 서버 배포
```bash
# 프로덕션 환경으로 실행
docker-compose -f docker-compose.prod.yml up -d
```

### AWS EC2 배포
1. AWS RDS PostgreSQL 인스턴스 생성
2. 환경 변수에서 `DATABASE_URL`을 RDS 엔드포인트로 변경
3. `docker-compose.prod.yml` 파일을 EC2에 업로드
4. Docker Compose로 실행

### AWS EKS CI/CD 배포
1. AWS EKS 클러스터 생성
2. GitHub Secrets 설정
3. 코드 푸시로 자동 배포
4. `https://api.yourdomain.com`에서 접근

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. Docker 컨테이너 상태: `docker-compose ps`
2. 로그 확인: `docker-compose logs backend`
3. 포트 충돌 확인: `lsof -i :8000`
4. 데이터베이스 연결 확인
5. Kubernetes 상태: `kubectl get pods -n witple`
6. GitHub Actions 로그: Repository → Actions 탭

---

**Witple Backend API** - FastAPI로 구축된 현대적인 백엔드 서버 🚀
