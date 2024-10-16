from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# FastAPI 경로 설정
@app.get("/")
async def read_root():
    return {"message": "Hello from LMM"}

# Lambda 핸들러
handler = Mangum(app)
