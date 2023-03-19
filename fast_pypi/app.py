from fastapi import FastAPI

from fast_pypi.router import pypi_router

app = FastAPI()
app.include_router(router=pypi_router)
