from fastapi import FastAPI
from app.domains.to_do_list.router import router as todo_router

app = FastAPI(title="Student To-Do App API")

# Connect the endpoints!
app.include_router(todo_router)

@app.get("/")
def health_check():
    return {"status": "Server is running perfectly!"}