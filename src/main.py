from fastapi import FastAPI

from db.utils import launch_db
from routers.user import router as users_router


launch_db()
app = FastAPI()

# Add routers
app.include_router(users_router)


@app.get("/")
def read_root():
    return "Server is running."
