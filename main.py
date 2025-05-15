import os
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

import logging
import uvicorn
from datetime import datetime


app = FastAPI()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# import routes
from routes.tone import router

app.include_router(router)

# Routes (example)
@app.get("/")
async def main_route():
    return {"message": "we are on tone voice api v1: we are live", "timestamp": str(datetime.now())}


# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)