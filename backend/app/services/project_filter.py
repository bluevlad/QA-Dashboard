"""단일 프로젝트(hopenvision) 연동 제한 필터.

QA Agent / To-be Agent 연동을 ``TARGET_PROJECT`` 한 곳으로 제한한다.
- ingest: 여러 프로젝트가 섞여 들어와도 타깃 데이터만 보존 (filter_ingest_to_target)
- fix-results / lifecycle verify: 타깃 외 프로젝트는 거부 (assert_target_project)

``TARGET_PROJECT`` 가 빈 문자열이면 제한이 비활성화된다(기존 다중 프로젝트 동작).
"""
import logging

from fastapi import HTTPException

from app.core.config import get_settings
from app.models.schemas import IngestRequest, RunSummaryIn

logger = logging.getLogger(__name__)


def _target_project() -> str:
    return get_settings().TARGET_PROJECT.strip()


def is_target_project(name: str | None) -> bool:
    """name 이 타깃 프로젝트면 True. 제한이 꺼져 있으면 항상 True (대소문자 무시)."""
    target = _target_project()
    if not target:
        return True
    return bool(name) and name.strip().lower() == target.lower()


def assert_target_project(name: str) -> None:
    """타깃 프로젝트가 아니면 HTTP 422. fix-results / lifecycle verify 가드용."""
    if not is_target_project(name):
        target = _target_project()
        raise HTTPException(
            status_code=422,
            detail=f"이 대시보드는 '{target}' 프로젝트만 허용합니다 (요청 프로젝트: '{name}')",
        )


def filter_ingest_to_target(req: IngestRequest) -> IngestRequest:
    """IngestRequest 를 타깃 프로젝트 데이터만 남기도록 필터링한다.

    여러 프로젝트가 섞여 들어와도 타깃 항목만 보존하고 run 단위 summary 카운트를
    재계산한다. ``failureDetails`` 는 ingest_run 의 filePath/suiteName 매칭 로직이
    프로젝트 범위를 처리하므로 그대로 둔다. 제한이 꺼져 있으면 원본을 반환한다.
    """
    target = _target_project()
    if not target:
        return req

    health = [h for h in req.healthResults if is_target_project(h.projectName)]
    tests = [t for t in req.testResults if is_target_project(t.projectName)]
    issues = [i for i in (req.issueResults or []) if is_target_project(i.projectName)]
    # projectName 이 없는 제안(전역 규칙)은 보존
    suggestions = [
        s
        for s in (req.suggestions or [])
        if s.projectName is None or is_target_project(s.projectName)
    ]

    dropped = {
        "healthResults": len(req.healthResults) - len(health),
        "testResults": len(req.testResults) - len(tests),
        "issueResults": len(req.issueResults or []) - len(issues),
        "suggestions": len(req.suggestions or []) - len(suggestions),
    }
    dropped = {k: v for k, v in dropped.items() if v}
    if dropped:
        logger.info(
            "Ingest %s: '%s' 외 프로젝트 데이터 제외 %s", req.runId, target, dropped
        )

    # run 단위 summary 를 필터링된 데이터 기준으로 재계산
    summary = RunSummaryIn(
        totalProjects=len(
            {h.projectName for h in health} | {t.projectName for t in tests}
        ),
        healthyProjects=sum(1 for h in health if h.healthy),
        testedProjects=sum(1 for t in tests if t.executed),
        totalTests=sum(t.total for t in tests),
        totalPassed=sum(t.passed for t in tests),
        totalFailed=sum(t.failed for t in tests),
        totalSkipped=sum(t.skipped for t in tests),
    )

    return req.model_copy(
        update={
            "healthResults": health,
            "testResults": tests,
            "issueResults": issues,
            "suggestions": suggestions,
            "summary": summary,
        }
    )
