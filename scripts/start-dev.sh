#!/bin/bash

echo "🚀 Witple Backend 개발 환경 시작 중..."

# 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo "📝 .env 파일이 없습니다. env.example을 복사합니다..."
    cp env.example .env
    echo "✅ .env 파일이 생성되었습니다."
fi

# Docker Compose로 개발 환경 실행
echo "🐳 Docker Compose로 개발 환경을 시작합니다..."
docker-compose up --build

echo "✅ 개발 환경이 시작되었습니다!"
echo "📚 API 문서: http://localhost:8000/docs"
echo "🏥 헬스체크: http://localhost:8000/api/v1/health"
