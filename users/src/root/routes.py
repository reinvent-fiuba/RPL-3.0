from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["Root"])


# root
@router.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")