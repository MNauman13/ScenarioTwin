from fastapi import FastAPI

app = FastAPI(title="ScenarioTwin Agent Orchestration", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}
