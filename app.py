from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as websocket_router, register_shutdown_handler

# Create FastAPI app instance
app = FastAPI()

# Allow cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router
app.include_router(websocket_router)

# Register graceful shutdown
register_shutdown_handler(app)
