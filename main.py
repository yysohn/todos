import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()

abs_path = os.path.dirname(os.path.realpath(__file__))
# html 템플릿 사용하기 위한 설정
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더와 연동하기 위한 설정
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"))

@app.get("/")
async def home(request: Request):
    todo = 30
    # html 파일에 데이터 렌더링해서 리턴한다는 의미
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "todo": todo}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)