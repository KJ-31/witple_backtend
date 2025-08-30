# GitHub Actions OIDC 설정 가이드

GitHub Actions에서 AWS EKS에 배포하기 위한 OIDC (OpenID Connect) 설정 방법을 안내합니다.

## 🔍 문제 상황

현재 발생하는 오류:
```
Error: Could not assume role with OIDC: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

이는 GitHub Actions의 OIDC provider와 EKS 클러스터의 OIDC provider가 다르기 때문입니다.

## 🛠️ 해결 방법

### 1단계: GitHub OIDC Provider 생성

AWS IAM에서 GitHub Actions용 OIDC provider를 생성합니다:

```bash
# GitHub OIDC Provider 생성
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --region ap-northeast-2
```

### 2단계: GitHub Actions IAM 역할 생성

```bash
# GitHub Actions용 IAM 정책 생성
cat > github-actions-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "eks:DescribeCluster",
        "eks:UpdateKubeconfig",
        "eks:CreateAccessEntry",
        "eks:DescribeAccessEntry",
        "eks:ListAccessEntries",
        "eks:DeleteAccessEntry",
        "sts:AssumeRoleWithWebIdentity"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# 정책 생성
aws iam create-policy \
  --policy-name GitHubActionsPolicy \
  --policy-document file://github-actions-policy.json \
  --region ap-northeast-2
```

### 3단계: Trust Policy 생성

`trust-policy-github-actions.json` 파일을 사용하여 trust policy를 생성합니다:

```bash
# GitHub Actions용 IAM 역할 생성
aws iam create-role \
  --role-name github-actions-role \
  --assume-role-policy-document file://trust-policy-github-actions.json \
  --region ap-northeast-2

# 정책 연결
aws iam attach-role-policy \
  --role-name github-actions-role \
  --policy-arn arn:aws:iam::737221504302:policy/GitHubActionsPolicy \
  --region ap-northeast-2
```

### 4단계: GitHub Repository 설정

GitHub Repository의 Settings → Secrets and variables → Actions에서 다음 시크릿을 추가:

```bash
AWS_ACCOUNT_ID=737221504302
```

### 5단계: Trust Policy 수정

`trust-policy-github-actions.json` 파일에서 다음 부분을 수정:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::737221504302:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/witple_backend:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

**중요**: `YOUR_GITHUB_USERNAME`을 실제 GitHub 사용자명으로 변경하세요.

### 6단계: EKS Access Entry 설정

GitHub Actions 역할에 EKS 클러스터 접근 권한을 부여합니다:

```bash
# EKS Access Entry 생성
aws eks create-access-entry \
  --cluster-name witple-cluster \
  --region ap-northeast-2 \
  --principal-arn "arn:aws:iam::737221504302:role/github-actions-role" \
  --type Standard \
  --kubernetes-groups system:masters
```

## 🔧 현재 설정 확인

### OIDC Provider 확인
```bash
# GitHub OIDC Provider 확인
aws iam list-open-id-connect-providers

# 특정 Provider 상세 정보
aws iam get-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::737221504302:oidc-provider/token.actions.githubusercontent.com
```

### IAM 역할 확인
```bash
# GitHub Actions 역할 확인
aws iam get-role --role-name github-actions-role

# 역할에 연결된 정책 확인
aws iam list-attached-role-policies --role-name github-actions-role
```

### EKS Access Entry 확인
```bash
# EKS Access Entry 목록 확인
aws eks list-access-entries \
  --cluster-name witple-cluster \
  --region ap-northeast-2
```

## 🚨 문제 해결

### 1. OIDC Provider가 이미 존재하는 경우
```bash
# 기존 Provider 삭제 후 재생성
aws iam delete-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::737221504302:oidc-provider/token.actions.githubusercontent.com
```

### 2. IAM 역할이 이미 존재하는 경우
```bash
# 기존 역할 삭제 후 재생성
aws iam delete-role --role-name github-actions-role
```

### 3. EKS Access Entry가 이미 존재하는 경우
```bash
# 기존 Access Entry 삭제 후 재생성
aws eks delete-access-entry \
  --cluster-name witple-cluster \
  --region ap-northeast-2 \
  --principal-arn "arn:aws:iam::737221504302:role/github-actions-role"
```

## 📝 참고 사항

1. **GitHub Repository 이름**: `witple_backtend`
2. **GitHub 사용자명**: `KJ-31`
3. **AWS 계정 ID**: `737221504302`로 설정됨
4. **EKS 클러스터명**: `witple-cluster`로 설정됨

## ✅ 설정 완료 후 테스트

GitHub Actions 워크플로우가 성공적으로 실행되는지 확인:

1. GitHub Repository에 코드 푸시
2. Actions 탭에서 워크플로우 실행 상태 확인
3. "Configure AWS credentials" 단계에서 오류가 없는지 확인

---

**OIDC 설정 완료!** 🎉

이제 GitHub Actions에서 AWS EKS에 안전하게 배포할 수 있습니다.
