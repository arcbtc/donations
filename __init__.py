import asyncio

from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import catch_everything_and_restart

db = Database("ext_donations")

donations_ext: APIRouter = APIRouter(prefix="/donations", tags=["Donations"])

donations_static_files = [
    {
        "path": "/donations/static",
        "app": StaticFiles(directory="lnbits/extensions/donations/static"),
        "name": "donations_static",
    }
]


def donations_renderer():
    return template_renderer(["lnbits/extensions/donations/templates"])

from .lnurl import *  # noqa
from .tasks import wait_for_paid_invoices
from .views import *  # noqa
from .views_api import *  # noqa


def donations_start():
    loop = asyncio.get_event_loop()
    loop.create_task(catch_everything_and_restart(wait_for_paid_invoices))
