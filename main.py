import os
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
from fastapi import Depends, FastAPI, Form, Request, status
from database import SessionLocal, engine, Base
import models

app = FastAPI()

# models에 정의한 모델클래스, 연결한 DB테이블 생성
Base.metadata.create_all(bind=engine)

# 의존성 주입을 위한 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 마지막에 무조건 닫음
        db.close()

abs_path = os.path.dirname(os.path.realpath(__file__))
# html 템플릿 사용하기 위한 설정
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더와 연동하기 위한 설정
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"))

@app.get("/")
async def home(request: Request, db : Session = Depends(get_db)):
    # todos 테이블 조화, 모든 todo를 조회
    todos = db.query(models.Todo).order_by(models.Todo.id.desc())
    for todo in todos:
        print(todo.id)
        print(todo.task)
    # html 파일에 데이터 렌더링해서 리턴한다는 의미
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "todos": todos}
    )

# 입력한 todo를 DB에 저장하기
@app.post("/add")
async def add(request: Request, task : str = Form(...), db : Session = Depends(get_db)):
    # DB에 저장하기
    # 클라이언트에서 넘어온 task데이터를 todo 객체로 만듦
    todo = models.Todo(task=task)
    # 클라이언트에서 넘어온 데이터를 테이블에 추가함
    db.add(todo)
    # 테이블에 적용
    db.commit()
    # todos 조회 수행하는 함수로 제어권 넘김
    # "home" : 다른 엔드포인트의 함수 이름
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

# todo 수정 : 
# 업데이트를 위한 조회와 수정데이터 적용 2개가 필요

# 127.0.0.1:8000/edit/6
@app.get("/edit/{todo_id}")
async def update(request: Request, todo_id: int, db : Session = Depends(get_db)):
    # DB에서 todo 클래스와 연결하고 조회
    # print("id :", id)
    todo = db.query(models.Todo).filter(models.Todo.id==todo_id).first()
    todos = db.query(models.Todo).order_by(models.Todo.id.desc())
    # print(todo)
    # 하여 리턴하기(편집가능한 html에 렌더링해서)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "todo": todo, "todos": todos}
    )

@app.post("/edit/{todo_id}")
async def update(request: Request, todo_id: int, task: str = Form(...), completed: bool = Form(False), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.task = task
    todo.completed = completed
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

# todo 삭제
@app.get("/delete/{todo_id}")
async def delete(request: Request, todo_id: int, db: Session = Depends(get_db)):    
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)