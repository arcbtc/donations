import asyncio

from loguru import logger

from lnbits.core.models import Payment
from lnbits.core.services import create_invoice, pay_invoice, websocketUpdater
from lnbits.core.views.api import api_wallet
from lnbits.helpers import get_current_extension_name
from lnbits.tasks import register_invoice_listener

from .crud import get_donation


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, get_current_extension_name())

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") != "donations":
        return

    donations_id = payment.extra.get("donationsId")

    donation = get_donation(donations_id)

    walletstuff = api_wallet(donation.wallet)

    logger.debug(walletstuff)
    
    return await websocketUpdater(donations_id, str(walletstuff.balance))

