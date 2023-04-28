from http import HTTPStatus

import httpx
from fastapi import Depends, Query
from lnurl import decode as decode_lnurl
from loguru import logger
from starlette.exceptions import HTTPException

from lnbits.core.crud import get_latest_payments_by_extension, get_user
from lnbits.core.models import Payment
from lnbits.core.services import create_invoice
from lnbits.core.views.api import api_payment
from lnbits.decorators import WalletTypeInfo, get_key_type, require_admin_key
from lnbits.settings import settings

from . import donations_ext
from .crud import create_donations, delete_donations, get_donation, get_donations
from .models import Donations


@donations_ext.get("/api/v1/donations", status_code=HTTPStatus.OK)
async def api_donations(
    all_wallets: bool = Query(False), wallet: WalletTypeInfo = Depends(get_key_type)
):
    wallet_ids = [wallet.wallet.id]
    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []

    return [donations.dict() for donations in await get_donations(wallet_ids)]


@donations_ext.post("/api/v1/donations", status_code=HTTPStatus.CREATED)
async def api_donations_create(
    data: Donations, wallet: WalletTypeInfo = Depends(get_key_type)
):
    donations = await create_donations(wallet_id=wallet.wallet.id, data=data)
    return donations.dict()


@donations_ext.delete("/api/v1/donations/{donations_id}")
async def api_donations_delete(
    donations_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)
):
    donations = await get_donation(donations_id)

    if not donations:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Donations does not exist."
        )

    if donations.wallet != wallet.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your Donations.")

    await delete_donations(donations_id)
    return "", HTTPStatus.NO_CONTENT