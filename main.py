# main.py
from fastapi import FastAPI
from routers import backtest

app = FastAPI()

# backtest 라우터 등록
app.include_router(backtest.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "V3"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
