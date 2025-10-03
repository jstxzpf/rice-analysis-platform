from fastapi import FastAPI
from app.api.v1 import endpoints
from app.db import base

# This line creates the database tables based on the models
# For schema updates, we use create_all with checkfirst=True
# In a production environment, you would typically use a migration tool like Alembic
base.Base.metadata.create_all(bind=base.engine)

app = FastAPI(
    title="江苏泰兴水稻长势智能分析平台",
    description="API for the Rice Growth Intelligent Analysis Platform.",
    version="1.0.0"
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Rice Analysis Platform API"}

app.include_router(endpoints.router, prefix="/api/v1")
app.include_router(endpoints.analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
