from fastapi import FastAPI, UploadFile, File, status, Response, Form 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from router import lmmCreate as create
from router import lmmEdit as edit
import json

# FastAPI 인스턴스 생성
app = FastAPI()

# 템플릿 설정 추가
templates = Jinja2Templates(directory="templates")

# 라우터 등록
app.include_router(create.router)
app.include_router(edit.router)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse, tags=['side'])
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/faq", response_class=HTMLResponse, tags=['side'])
async def faq(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse, tags=['side'])
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/test")
async def test(request: str):
    return {"message": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8000)

handler = Mangum(app, lifespan="auto")