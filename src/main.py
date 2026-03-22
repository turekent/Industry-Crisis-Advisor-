"""产业避险参谋 - 主服务"""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="产业避险参谋")

@app.get("/")
async def root():
    return {"message": "产业避险参谋 API 服务运行中"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
