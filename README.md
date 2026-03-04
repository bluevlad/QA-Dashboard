# QA-Dashboard

QA 테스트 결과를 수집, 시각화, 관리하는 풀스택 웹 애플리케이션입니다.
CI/CD 파이프라인에서 생성된 테스트 실행 로그를 자동으로 수집하고, 프로젝트별 헬스체크, 테스트 통과율, 트렌드를 대시보드로 제공합니다.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite 5, Ant Design 5, Recharts |
| **Backend** | FastAPI, Python 3.11, Uvicorn, APScheduler |
| **Database** | PostgreSQL (asyncpg) |
| **Deployment** | Docker, Docker Compose, GitHub Actions, Nginx |

## Project Structure

```
QA-Dashboard/
├── frontend/                    # React + TypeScript + Vite
│   ├── src/
│   │   ├── pages/               # Dashboard, API Guide 페이지
│   │   ├── components/          # Layout, Charts, Dashboard 컴포넌트
│   │   ├── constants/           # API 엔드포인트 정의
│   │   └── types/               # TypeScript 인터페이스
│   ├── Dockerfile               # Multi-stage (Node → Nginx)
│   └── nginx.conf
├── backend/                     # FastAPI + asyncpg
│   ├── app/
│   │   ├── api/                 # API 라우터 (6개 모듈)
│   │   ├── models/              # DB 스키마 & Pydantic 모델
│   │   ├── services/            # 비즈니스 로직 (5개 서비스)
│   │   └── core/                # 설정, DB 커넥션, 스케줄러
│   ├── Dockerfile               # Python 3.11 slim
│   └── requirements.txt
├── docker-compose.prod.yml      # 프로덕션 오케스트레이션
├── .github/workflows/           # CI/CD 파이프라인
└── .env.example                 # 환경변수 템플릿
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | 서버 상태 확인 |
| `GET` | `/api/summary` | 대시보드 요약 데이터 |
| `GET` | `/api/runs` | 실행 목록 (페이징) |
| `GET` | `/api/runs/{run_id}` | 실행 상세 정보 |
| `GET` | `/api/projects` | 프로젝트 목록 및 최신 상태 |
| `GET` | `/api/projects/{name}/history` | 프로젝트별 히스토리 |
| `GET` | `/api/trends/pass-rate` | 일별 테스트 통과율 추이 |
| `GET` | `/api/trends/duration` | 일별 테스트 소요시간 추이 |
| `POST` | `/api/import/run` | 단일 실행 데이터 임포트 |
| `POST` | `/api/import/bulk` | 다건 일괄 임포트 |
| `DELETE` | `/api/runs/{run_id}` | 실행 데이터 삭제 |

## Database Schema

5개의 핵심 테이블로 구성됩니다.

- **scheduler_runs** - 테스트 실행 메인 레코드
- **health_check_results** - 프로젝트별 헬스체크 결과
- **endpoint_check_results** - 개별 엔드포인트 체크 결과
- **test_run_results** - 프로젝트별 테스트 실행 결과 (pass/fail/skip)
- **issue_report_results** - GitHub 이슈 리포팅 결과

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL
- Docker & Docker Compose (프로덕션 배포 시)

### Environment Setup

```bash
cp .env.example .env
# .env 파일을 환경에 맞게 수정
```

```env
QD_DB_HOST=localhost
QD_DB_PORT=5432
QD_DB_NAME=qa_dashboard
QD_DB_USER=postgres
QD_DB_PASSWORD=your_secure_password_here
QD_LOG_DIR=/app/logs
QD_SYNC_INTERVAL=60
QD_CORS_ORIGINS=http://localhost:4095
```

### Local Development

**Backend**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9095
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:4095
- Backend API: http://localhost:9095

### Production Deployment (Docker)

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## CI/CD

GitHub Actions를 통해 `prod` 브랜치에 푸시 시 자동 배포됩니다.

1. GitHub Secrets에서 `.env` 파일 생성
2. 기존 컨테이너 중지 및 제거
3. PostgreSQL 연결 확인
4. Docker 이미지 빌드 및 컨테이너 기동
5. 헬스체크 (Backend `/api/health`, Frontend `:4095`)
6. 미사용 Docker 이미지 정리

## Key Features

- **자동 로그 수집** - 지정된 디렉토리에서 `run-*.json` 파일을 주기적으로 스캔하여 자동 임포트
- **대시보드** - 프로젝트별 헬스체크 상태, 테스트 통과율, 트렌드 시각화
- **API 가이드** - 내장된 API 문서 페이지 (cURL, Python, JavaScript 예제 제공)
- **비동기 처리** - FastAPI + asyncpg 기반의 완전한 비동기 아키텍처
- **트랜잭션 보장** - 데이터 임포트 시 트랜잭션 단위 처리
