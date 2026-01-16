from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Furniture Shop Refund Microservice",
    description="Customer support and refund processing system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Furniture Shop Refund Microservice API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "refund-microservice"}


@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse

    return FileResponse("src/static/favicon.ico")
