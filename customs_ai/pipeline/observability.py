"""可观测性工具（与之前项目同款设计）。"""
import json
import logging
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from customs_ai.config import settings

logger = logging.getLogger("customs_ai")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", datefmt="%H:%M:%S"
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class StepTrace:
    def __init__(self, name: str):
        self.name = name
        self.started_at: float | None = None
        self.duration_ms: int | None = None
        self.status: str = "pending"
        self.meta: dict[str, Any] = {}

    def start(self):
        self.started_at = time.perf_counter()
        self.status = "running"
        logger.info(f"[{self.name}] 开始")

    def finish_ok(self, meta=None):
        self._close("success", meta)

    def finish_err(self, err: str):
        self.meta["error"] = err
        self._close("failed", None)

    def _close(self, status, meta):
        assert self.started_at is not None
        self.duration_ms = int((time.perf_counter() - self.started_at) * 1000)
        self.status = status
        if meta:
            self.meta.update(meta)
        icon = "OK " if status == "success" else "ERR"
        logger.info(f"[{self.name}] {icon} 耗时={self.duration_ms}ms {self.meta}")


class PipelineTrace:
    def __init__(self, job_id=None, source=""):
        self.job_id = job_id or uuid.uuid4().hex[:8]
        self.source = source
        self.steps: list[StepTrace] = []

    @contextmanager
    def step(self, name: str):
        tr = StepTrace(name)
        self.steps.append(tr)
        tr.start()
        try:
            yield tr
            if tr.status == "running":
                tr.finish_ok()
        except Exception as e:
            tr.finish_err(str(e))
            raise

    def summary(self):
        return {
            "job_id": self.job_id,
            "source": self.source,
            "total_ms": sum(s.duration_ms or 0 for s in self.steps),
            "steps": [
                {"name": s.name, "status": s.status, "duration_ms": s.duration_ms, "meta": s.meta}
                for s in self.steps
            ],
        }

    def save(self, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "trace.json"
        path.write_text(json.dumps(self.summary(), ensure_ascii=False, indent=2))
        return path
