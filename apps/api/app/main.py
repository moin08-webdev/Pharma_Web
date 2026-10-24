import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppException, app_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup verification
    print(f"[{settings.APP_NAME}] Starting up in {settings.APP_ENV} mode...")
    yield
    print(f"[{settings.APP_NAME}] Shutting down cleanly.")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-assisted prescription fulfilment workspace for Indian pharmacies",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = req_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handler
app.add_exception_handler(AppException, app_exception_handler)

# Mount API
app.include_router(api_router, prefix="/api")
