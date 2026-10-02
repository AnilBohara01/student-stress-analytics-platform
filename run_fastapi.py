import sys
import os
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting FastAPI Student Stress Analytics Microservice...")
    print("📍 Interactive Swagger API Docs: http://127.0.0.1:8001/docs")
    print("📍 ReDoc Documentation: http://127.0.0.1:8001/redoc")
    print("📍 Health Check: http://127.0.0.1:8001/health\n")
    
    uvicorn.run(
        "fastapi_app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
