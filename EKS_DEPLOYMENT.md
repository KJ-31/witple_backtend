# EKS + GitHub Actions CI/CD 배포 가이드

Witple Backend API를 AWS EKS에 GitHub Actions로 자동 배포하는 방법을 안내합니다.

## 🚀 **1단계: AWS EKS 클러스터 생성**

### EKS 클러스터 생성
```bash
# eksctl 설치
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# EKS 클러스터 생성
eksctl create cluster \
  --name witple-cluster \
  --region ap-northeast-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed
```

### 클러스터 확인
```bash
# 클러스터 상태 확인
eksctl get cluster --region ap-northeast-2

# kubeconfig 업데이트
aws eks update-kubeconfig --region ap-northeast-2 --name witple-cluster

# 노드 확인
kubectl get nodes
```

## 🗄️ **2단계: AWS RDS PostgreSQL 설정**

### RDS 인스턴스 생성
```bash
# AWS Console → RDS → 데이터베이스 생성
- 엔진: PostgreSQL
- 템플릿: 프로덕션
- 인스턴스 크기: db.t3.small
- 스토리지: 20GB
- 데이터베이스 이름: witple
- 마스터 사용자: witple_user
- 마스터 암호: 안전한 비밀번호
```

### 보안 그룹 설정
```bash
# RDS 보안 그룹에 EKS 보안 그룹 추가
# 인바운드 규칙: PostgreSQL (5432) - EKS 보안 그룹
```

## 🐳 **3단계: Amazon ECR 리포지토리 생성**

### ECR 리포지토리 생성
```bash
# ECR 리포지토리 생성
aws ecr create-repository \
  --repository-name witple-backend \
  --region ap-northeast-2

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com
```

## 🔐 **4단계: GitHub Secrets 설정**

### GitHub Repository → Settings → Secrets and variables → Actions

다음 시크릿들을 추가:

```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
SECRET_KEY=your-super-secret-key-for-production
DATABASE_URL=postgresql://witple_user:password@your-rds-endpoint:5432/witple
REDIS_URL=redis://your-redis-endpoint:6379
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🏗️ **5단계: Kubernetes 리소스 배포**

### 네임스페이스 및 기본 리소스 생성
```bash
# 네임스페이스 생성
kubectl apply -f k8s/namespace.yaml

# ECR 인증을 위한 Secret 생성
kubectl create secret docker-registry regcred \
  --docker-server=$AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region ap-northeast-2) \
  --namespace=witple
```

### ConfigMap 및 Secret 생성
```bash
# ConfigMap 생성 (GitHub Actions에서 자동 업데이트됨)
kubectl apply -f k8s/configmap.yaml

# Secret 생성 (GitHub Actions에서 자동 업데이트됨)
kubectl apply -f k8s/secret.yaml
```

## 🌐 **6단계: ALB Ingress Controller 설치**

### ALB Ingress Controller 설치
```bash
# IAM 정책 생성
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.4/docs/install/iam_policy.json
aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# IAM 역할 생성
eksctl create iamserviceaccount \
  --cluster=witple-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name AmazonEKSLoadBalancerControllerRole \
  --attach-policy-arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve

# Helm으로 ALB Ingress Controller 설치
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=witple-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

## 🔄 **7단계: CI/CD 파이프라인 테스트**

### 코드 푸시로 배포 테스트
```bash
# main 브랜치에 코드 푸시
git add .
git commit -m "Initial EKS deployment setup"
git push origin main
```

### GitHub Actions 확인
1. GitHub Repository → Actions 탭
2. 워크플로우 실행 상태 확인
3. 각 단계별 로그 확인

## 📊 **8단계: 모니터링 및 관리**

### 배포 상태 확인
```bash
# 파드 상태 확인
kubectl get pods -n witple

# 서비스 확인
kubectl get services -n witple

# Ingress 확인
kubectl get ingress -n witple

# HPA 상태 확인
kubectl get hpa -n witple
```

### 로그 확인
```bash
# 애플리케이션 로그
kubectl logs -f deployment/witple-backend -n witple

# ALB Ingress Controller 로그
kubectl logs -f deployment/aws-load-balancer-controller -n kube-system
```

## 🔒 **9단계: SSL 인증서 설정**

### AWS Certificate Manager에서 인증서 생성
```bash
# AWS Console → Certificate Manager → 인증서 요청
# 도메인: api.yourdomain.com
# 검증 방법: DNS 검증 또는 이메일 검증
```

### Ingress에 인증서 적용
```bash
# k8s/ingress.yaml 파일에서 certificate-arn 수정
# arn:aws:acm:ap-northeast-2:$AWS_ACCOUNT_ID:certificate/$CERTIFICATE_ID
```

## 📈 **10단계: 스케일링 및 성능 최적화**

### 자동 스케일링 확인
```bash
# HPA 상태 확인
kubectl describe hpa witple-backend-hpa -n witple

# 리소스 사용량 확인
kubectl top pods -n witple
```

### 성능 모니터링
```bash
# Prometheus + Grafana 설치 (선택사항)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

## 🚨 **문제 해결**

### 일반적인 문제들

1. **이미지 풀 오류**
   ```bash
   # ECR 인증 확인
   kubectl describe pod <pod-name> -n witple
   ```

2. **데이터베이스 연결 오류**
   ```bash
   # RDS 보안 그룹 확인
   # EKS 노드 보안 그룹에서 RDS로의 접근 허용
   ```

3. **ALB 생성 실패**
   ```bash
   # ALB Ingress Controller 로그 확인
   kubectl logs -f deployment/aws-load-balancer-controller -n kube-system
   ```

### 디버깅 명령어
```bash
# 파드 상세 정보
kubectl describe pod <pod-name> -n witple

# 이벤트 확인
kubectl get events -n witple --sort-by='.lastTimestamp'

# 네트워크 정책 확인
kubectl get networkpolicies -n witple
```

## 💰 **비용 최적화**

### 비용 절약 팁
```bash
# 노드 그룹 스케일링
eksctl scale nodegroup --cluster=witple-cluster --name=standard-workers --nodes=1 --nodes-min=1 --nodes-max=2

# 스팟 인스턴스 사용
eksctl create nodegroup --cluster=witple-cluster --spot --instance-types=t3.medium
```

---

**EKS + GitHub Actions CI/CD 배포 완료!** 🎉

이제 `https://api.yourdomain.com`에서 API에 접근할 수 있습니다.
