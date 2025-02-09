from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


app.include_router(router, prefix="/api", tags=["Invoice-Receipt-Extraction"])


@app.get("/")
async def root():
    return {
        "message": "Invoice and Receipt Extraction API routes: /api/extract-invoice, /api/extract-receipt"
    }
