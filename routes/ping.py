from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

healthcheck_router = APIRouter()

# token_auth_scheme=HTTPBearer()

@healthcheck_router.get("/ping")
def ping():
    return "pong"


# @healthcheck_router.get("/pping")
# def pping(token: str = Depends(token_auth_scheme)):
#     print(token)
#     return "ppong"