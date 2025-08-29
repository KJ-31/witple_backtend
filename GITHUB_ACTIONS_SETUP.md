# GitHub Actions + EKS CI/CD 설정 가이드

테라폼으로 관리하는 EKS 클러스터에 GitHub Actions로 자동 배포하는 설정 방법입니다.

## 🔐 **1단계: GitHub Secrets 설정**

### GitHub Repository → Settings → Secrets and variables → Actions

다음 시크릿들을 추가:

```bash
# AWS 계정 정보
AWS_ACCOUNT_ID=471303021447

# 애플리케이션 설정
SECRET_KEY=your-super-secret-key-for-production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 데이터베이스 설정
DATABASE_URL=postgresql://witple_user:password@your-rds-endpoint:5432/witple
REDIS_URL=redis://your-redis-endpoint:6379

# 도메인 설정 (선택사항)
DOMAIN_NAME=yourdomain.com
```

## 🏗️ **2단계: 테라폼에서 필요한 리소스들**

### IAM Role for GitHub Actions
```hcl
# GitHub Actions용 IAM Role 생성
resource "aws_iam_role" "github_actions" {
  name = "github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${var.aws_account_id}:oidc-provider/token.actions.githubusercontent.com"
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:your-username/witple_backend:*"
          }
        }
      }
    ]
  })
}

# ECR 권한
resource "aws_iam_role_policy_attachment" "github_actions_ecr" {
  role       = aws_iam_role.github_actions.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

# EKS 권한
resource "aws_iam_role_policy_attachment" "github_actions_eks" {
  role       = aws_iam_role.github_actions.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# 추가 권한 (필요시)
resource "aws_iam_role_policy" "github_actions_additional" {
  name = "github-actions-additional"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:UpdateKubeconfig",
          "eks:CreateAccessEntry",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups"
        ]
        Resource = "*"
      }
    ]
  })
}
```

### ECR Repository
```hcl
# ECR 리포지토리 생성
resource "aws_ecr_repository" "witple_backend" {
  name                 = "witple-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
```

### EKS Cluster (기존)
```hcl
# 기존 EKS 클러스터에 ALB Ingress Controller 설치
resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"

  set {
    name  = "clusterName"
    value = aws_eks_cluster.witple_cluster.name
  }

  set {
    name  = "serviceAccount.create"
    value = "false"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  depends_on = [aws_eks_cluster.witple_cluster]
}
```

## 🚀 **3단계: 배포 테스트**

### 코드 푸시로 배포
```bash
# main 브랜치에 푸시
git add .
git commit -m "Initial EKS deployment setup"
git push origin main
```

### GitHub Actions 확인
1. GitHub Repository → Actions 탭
2. "CI/CD Pipeline - Backend" 워크플로우 실행 확인
3. 각 단계별 로그 확인

## 📊 **4단계: 배포 상태 확인**

### EKS 클러스터에서 확인
```bash
# kubeconfig 업데이트
aws eks update-kubeconfig --name witple-cluster --region ap-northeast-2

# 네임스페이스 확인
kubectl get namespace witple

# 파드 상태 확인
kubectl get pods -n witple

# 서비스 확인
kubectl get services -n witple

# Ingress 확인
kubectl get ingress -n witple

# 로그 확인
kubectl logs -f deployment/witple-backend -n witple
```

### ALB DNS 확인
```bash
# ALB DNS 이름 가져오기
ALB_DNS=$(kubectl get ingress witple-backend-ingress -n witple -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "ALB DNS: $ALB_DNS"

# API 테스트
curl http://$ALB_DNS/api/v1/health
```

## 🔧 **5단계: 환경별 설정**

### 개발 환경 (선택사항)
```bash
# develop 브랜치용 별도 워크플로우 생성 가능
# 네임스페이스: witple-dev
# 리플리카: 1개
# 리소스: 최소
```

### 프로덕션 환경
```bash
# main 브랜치용 (현재 설정)
# 네임스페이스: witple
# 리플리카: 3개 (HPA로 자동 스케일링)
# 리소스: 충분한 할당
```

## 🚨 **6단계: 문제 해결**

### 일반적인 문제들

1. **EKS Access Entry 오류**
   ```bash
   # EKS Access Entry 확인
   aws eks list-access-entries --cluster-name witple-cluster --region ap-northeast-2
   
   # 수동으로 Access Entry 생성
   aws eks create-access-entry \
     --cluster-name witple-cluster \
     --region ap-northeast-2 \
     --principal-arn "arn:aws:iam::471303021447:role/github-actions-role" \
     --type Standard \
     --kubernetes-groups system:masters
   ```

2. **ECR 권한 오류**
   ```bash
   # ECR 리포지토리 확인
   aws ecr describe-repositories --repository-names witple-backend
   
   # ECR 로그인 테스트
   aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 471303021447.dkr.ecr.ap-northeast-2.amazonaws.com
   ```

3. **ALB Ingress Controller 오류**
   ```bash
   # ALB Ingress Controller 상태 확인
   kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
   
   # 로그 확인
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

# ConfigMap 확인
kubectl get configmap app-config -n witple -o yaml

# Secret 확인
kubectl get secret db-secret -n witple -o yaml
```

## 📈 **7단계: 모니터링 및 스케일링**

### HPA 상태 확인
```bash
# HPA 상태 확인
kubectl get hpa -n witple

# HPA 상세 정보
kubectl describe hpa witple-backend-hpa -n witple

# 리소스 사용량 확인
kubectl top pods -n witple
```

### 로그 모니터링
```bash
# 실시간 로그 확인
kubectl logs -f deployment/witple-backend -n witple

# 특정 파드 로그 확인
kubectl logs <pod-name> -n witple
```

## 💰 **8단계: 비용 최적화**

### 리소스 최적화
```bash
# HPA 설정 조정
kubectl patch hpa witple-backend-hpa -n witple -p '{"spec":{"minReplicas":2,"maxReplicas":5}}'

# 리소스 요청/제한 조정
kubectl patch deployment witple-backend -n witple -p '{"spec":{"template":{"spec":{"containers":[{"name":"witple-backend","resources":{"requests":{"memory":"128Mi","cpu":"100m"},"limits":{"memory":"256Mi","cpu":"200m"}}}]}}}}'
```

---

**GitHub Actions + EKS CI/CD 설정 완료!** 🎉

이제 `git push origin main`으로 코드를 푸시하면 자동으로 EKS에 배포됩니다.
