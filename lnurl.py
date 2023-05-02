import hashlib
import json
from http import HTTPStatus

from fastapi import Request
from fastapi.param_functions import Query
from lnurl.types import LnurlPayMetadata
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from lnbits.core.services import create_invoice

from . import donations_ext
from .crud import get_donation


@donations_ext.get(
    "/lnurl/{donation_id}", response_class=HTMLResponse, name="donation.lnurl_response"
)
async def lnurl_response(req: Request, donation_id: str):
    donation = await get_donation(donation_id)
    if not donation:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Donation not found"
        )

    payResponse = {
        "tag": "payRequest",
        "callback": req.url_for("donation.lnurl_callback", donation_id=donation_id),
        "metadata": LnurlPayMetadata(json.dumps([["text/plain", str(donation.title)]])),
        "maxSendable": 500000000,
        "minSendable": 10000,
    }
    return json.dumps(payResponse)


@donations_ext.get(
    "/lnurl/cb/{donation_id}", response_class=HTMLResponse, name="donation.lnurl_callback"
)
async def lnurl_callback(
    donation_id: str, amount: str = Query(None)
):
    donation = await get_donation(donation_id)
    if not donation:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Donation not found"
        )
    amount_received = int(amount)

    if amount_received < 10000:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Amount {round(amount_received / 1000)} is smaller than minimum 10 sats.",
        )
    elif amount_received / 1000 > 500000000:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Amount {round(amount_received / 1000)} is greater than maximum 500000.",
        )
    _, payment_request = await create_invoice(
        wallet_id=donation.wallet,
        amount=int(amount_received / 1000),
        memo=donation.title,
        unhashed_description=(
            LnurlPayMetadata(json.dumps([["text/plain", str(donation.title)]]))
        ).encode(),
        extra={"tag": "donations", "donationsId": donation_id},
    )
    payResponse = {"pr": payment_request, "routes": []}
    return json.dumps(payResponse)