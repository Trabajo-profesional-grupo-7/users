from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.db import models
from app.db.database import engine
from app.routes.auth_router import router as auth_router
from app.routes.password_router import router as password_router
from app.routes.user_router import router as user_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Users",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(password_router)


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")
