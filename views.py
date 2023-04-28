from http import HTTPStatus

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse

from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.settings import settings

from . import donations_ext, donations_renderer
from .crud import get_donation
from loguru import logger
templates = Jinja2Templates(directory="templates")


@donations_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return donations_renderer().TemplateResponse(
        "donations/index.html", {"request": request, "user": user.dict()}
    )


@donations_ext.get("/{donations_id}")
async def donations(request: Request, donations_id):
    donations = await get_donation(donations_id)
    if not donations:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Donations does not exist."
        )

    return donations_renderer().TemplateResponse(
        "donations/donations.html",
        {
            "request": request,
            "donation": donations.id,
            "title": donations.title,
            "description": donations.description,
        },
    )