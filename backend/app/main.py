from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SaaS Shopper Management System",
    description="API para la gestión de pedidos, clientes y facturación de la Shoper",
    version="1.0.0"
)

from app.presentation.api_v1.api import api_router

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}
