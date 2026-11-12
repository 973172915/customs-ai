"""FastAPI 接口。"""
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from customs_ai.config import settings
from customs_ai.pipeline.graph import export_mermaid, run_document_parse, run_knowledge_qa

app = FastAPI(title="CustomsAI", description="关务智能助手", version="0.1.0")


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    session_id: str | None = None


@app.post("/api/ask")
def ask(req: QueryRequest):
    """知识库问答（带出处）。"""
    try:
        result = run_knowledge_qa(req.query, req.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(result)


@app.post("/api/parse")
async def parse(file: UploadFile = File(...)):
    """上传文档解析。"""
    save_dir = settings.output_dir / "uploads"
    save_dir.mkdir(parents=True, exist_ok=True)
    path = save_dir / file.filename
    with open(path, "wb") as f:
        f.write(file.file.read())

    try:
        result = run_document_parse(str(path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(result)


@app.get("/api/graph/mermaid")
def graph_mermaid():
    return {"mermaid": export_mermaid()}


@app.get("/api/health")
def health():
    return {"status": "ok"}
