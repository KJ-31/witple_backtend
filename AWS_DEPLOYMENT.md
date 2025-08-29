# AWS 배포 가이드

Witple Backend API를 AWS에 배포하는 방법을 안내합니다.

## 🚀 AWS 서비스 구성

### 1. AWS RDS PostgreSQL 설정

1. **RDS 인스턴스 생성**
   ```bash
   # AWS Console에서 RDS > 데이터베이스 > 데이터베이스 생성
   - 엔진: PostgreSQL
   - 템플릿: 개발/테스트 또는 프로덕션
   - 인스턴스 크기: db.t3.micro (테스트용) / db.t3.small (프로덕션용)
   - 스토리지: 20GB (필요에 따라 조정)
   - 가용성: 단일 AZ (테스트용) / 다중 AZ (프로덕션용)
   ```

2. **데이터베이스 설정**
   ```bash
   - 데이터베이스 이름: witple
   - 마스터 사용자 이름: witple_user
   - 마스터 암호: 안전한 비밀번호 설정
   ```

3. **보안 그룹 설정**
   ```bash
   # 인바운드 규칙 추가
   - 유형: PostgreSQL
   - 포트: 5432
   - 소스: EC2 보안 그룹 또는 특정 IP
   ```

### 2. EC2 인스턴스 설정

1. **EC2 인스턴스 생성**
   ```bash
   # Ubuntu 22.04 LTS 권장
   - 인스턴스 유형: t3.micro (테스트용) / t3.small (프로덕션용)
   - 스토리지: 8GB (필요에 따라 조정)
   ```

2. **보안 그룹 설정**
   ```bash
   # 인바운드 규칙
   - SSH (22): 특정 IP에서만 접근
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0 (SSL 인증서 사용 시)
   - Custom TCP (8000): 0.0.0.0/0 (API 포트)
   ```

## 🔧 배포 과정

### 1. EC2 인스턴스 준비

```bash
# EC2에 SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 재로그인
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. 애플리케이션 배포

```bash
# 프로젝트 클론
git clone https://github.com/your-username/witple_backend.git
cd witple_backend

# 환경 변수 설정
cp env.example .env
nano .env
```

### 3. 환경 변수 수정

```bash
# .env 파일 수정
ENVIRONMENT=production
DATABASE_URL=postgresql://witple_user:your-password@your-rds-endpoint:5432/witple
SECRET_KEY=your-super-secret-key-for-production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. 프로덕션 배포

```bash
# 프로덕션 환경 실행 (PostgreSQL 서비스 제거)
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f backend
```

## 🔒 보안 설정

### 1. SSL/TLS 인증서 (권장)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# Nginx 설정
sudo nano /etc/nginx/sites-available/witple
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com

# Nginx 활성화
sudo ln -s /etc/nginx/sites-available/witple /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. 방화벽 설정

```bash
# UFW 활성화
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 8000
```

## 📊 모니터링

### 1. 로그 모니터링

```bash
# 애플리케이션 로그
docker-compose -f docker-compose.prod.yml logs -f backend

# 시스템 로그
sudo journalctl -u docker.service -f
```

### 2. 성능 모니터링

```bash
# 시스템 리소스 확인
htop
df -h
docker stats
```

## 🔄 백업 및 복구

### 1. RDS 백업

```bash
# AWS Console에서 자동 백업 설정
# 백업 보존 기간: 7일 (테스트용) / 30일 (프로덕션용)
# 백업 윈도우: 유지보수 윈도우와 동일하게 설정
```

### 2. 애플리케이션 백업

```bash
# 환경 변수 백업
cp .env .env.backup

# Docker 이미지 백업
docker save witple_backend:latest > witple_backend.tar
```

## 🚨 문제 해결

### 1. 데이터베이스 연결 오류

```bash
# RDS 엔드포인트 확인
aws rds describe-db-instances --query 'DBInstances[*].[Endpoint]'

# 연결 테스트
psql -h your-rds-endpoint -U witple_user -d witple
```

### 2. 포트 충돌

```bash
# 포트 사용 확인
sudo netstat -tlnp | grep :8000

# 프로세스 종료
sudo kill -9 <PID>
```

### 3. 메모리 부족

```bash
# 스왑 메모리 추가
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📈 스케일링

### 1. 수평 스케일링

```bash
# 로드 밸런서 설정
# EC2 인스턴스 여러 개 실행
# Auto Scaling Group 설정
```

### 2. 수직 스케일링

```bash
# EC2 인스턴스 크기 증가
# RDS 인스턴스 크기 증가
```

---

**AWS 배포 완료!** 🎉

이제 `https://yourdomain.com`에서 API에 접근할 수 있습니다.
