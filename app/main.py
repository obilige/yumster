# default lib
import os
# from dotenv import load_dotenv
from uuid import uuid4

# fast-api
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

# router
from api.question.question import question 
from api.vector.vector import vector
from api.operation.operation import operation

# server
import uvicorn

# load .env & set root path
# APP_ROOT = os.path.dirname(__file__)
# dotenv_path = os.path.join(APP_ROOT, '.env')
# load_dotenv(dotenv_path, override=True)

# api setting
app = FastAPI()
app.include_router(question)
app.include_router(operation)
app.include_router(vector)

# AuthJWT configuration settings
class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv('JWT_SECRET_KEY', 'BE-EAGLE SECRET')

@AuthJWT.load_config
def get_config():
    return Settings()

# Exception handlers
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )



# API for token
@app.get("/check")
async def _check():
    return {"code": 200, "message": "I AM LIVING", "data": ""}

@app.get("/hello")
async def _hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        identify = str(uuid4())
        access_token = Authorize.create_access_token(subject=identify)
        refresh_token = Authorize.create_refresh_token(subject=identify)
        return {"code": 200, "message": "hello", "data": "", "access_token": access_token, "refresh_token": refresh_token}

    return {"code": 200, "message": "hello", "data": ""}

@app.get("/refresh")
async def _refresh(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    current_user = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=current_user)
    return {"code": 200, "message": "refresh", "data": "", "access_token": access_token}



# Run API server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)