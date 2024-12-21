from fastapi import FastAPI
from routes import router

app = FastAPI()

#including routes

app.include_router(router)

@app.get('/')
def read_root():
    return {
        'message': 'Welcom to the todo list API'
    }
