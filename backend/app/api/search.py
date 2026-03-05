from fastapi import APIRouter, Query

from app.core.database import get_pool

router = APIRouter()


@router.get("/search")
async def search(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    pool = await get_pool()
    tsquery = " & ".join(q.split())

    async with pool.acquire() as conn:
        failure_rows = await conn.fetch(
            """
            SELECT fd.id, fd.test_name, fd.error_message, fd.suite_name,
                   r.run_id, ts_rank(fd.search_vector, to_tsquery('simple', $1)) as rank
            FROM qa_failure_details fd
            JOIN qa_test_results tr ON tr.id = fd.test_result_id
            JOIN qa_runs r ON r.id = tr.run_id
            WHERE fd.search_vector @@ to_tsquery('simple', $1)
            ORDER BY rank DESC
            LIMIT $2
            """,
            tsquery,
            limit,
        )

    results = []
    for r in failure_rows:
        results.append({
            "type": "failure",
            "id": r["id"],
            "runId": r["run_id"],
            "text": f"{r['test_name']}: {r['error_message'] or ''}",
            "rank": float(r["rank"]),
        })

    return {"query": q, "total": len(results), "results": results}
