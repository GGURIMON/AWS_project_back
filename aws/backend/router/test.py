from fastapi import APIRouter

router = APIRouter(prefix="/test", tags = ['test'])

@router.get("/")
def testing():
    return {"message": "if you are watching this? you are successed!"}
