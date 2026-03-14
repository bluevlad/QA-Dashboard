# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> 도메인/URL/포트 규칙: [DOMAIN_MANAGEMENT.md](https://github.com/bluevlad/Claude-Opus-bluevlad/blob/main/standards/infrastructure/DOMAIN_MANAGEMENT.md) — `https://도메인:포트` 사용 금지

## Project Overview

QA Dashboard - Autonomous QA Agent 실행 결과 시각화 및 생명주기 추적 대시보드

## Environment

- **Backend**: Python 3 / FastAPI 0.115 / Uvicorn (포트 9095)
- **Frontend**: React 18 / TypeScript / Vite 5 / Ant Design 5 (포트 4095)
- **Database**: PostgreSQL (asyncpg, DB명: `qa_dashboard`)
- **Target Server**: MacBook Docker (172.30.1.72) / Windows 로컬 개발

## Help Page 관리

> 작성 표준: [HELP_PAGE_GUIDE.md](https://github.com/bluevlad/Claude-Opus-bluevlad/blob/main/standards/documentation/HELP_PAGE_GUIDE.md)
> HTML 템플릿: [help-page-template.html](https://github.com/bluevlad/Claude-Opus-bluevlad/blob/main/standards/documentation/templates/help-page-template.html)

- **기능 추가/변경/삭제 시 반드시 헬프 페이지도 함께 업데이트**
- 헬프 파일 위치: `frontend/public/help/`
- 서비스 accent-color: `#ec4899` (Pink)
- 대상 가이드 파일:
  - `user-guide.html` — QA 대시보드 사용 가이드
  - `api-guide.html` — QA Dashboard API 가이드

## Do NOT

- .env 파일 커밋 금지
- 운영 Docker 컨테이너 직접 조작 금지
- 운영 DB에 직접 DROP/TRUNCATE 실행 금지
- 서버 주소, 비밀번호 추측 금지 — 반드시 확인 후 사용
