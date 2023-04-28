from typing import List, Optional, Union

from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import Donations, Donations
from loguru import logger

async def create_donations(wallet_id: str, data: Donations) -> Donations:
    donations_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO donations.donations (id, wallet, title, description)
        VALUES (?, ?, ?, ?)
        """,
        (
            donations_id,
            wallet_id,
            data.title,
            data.description,
        ),
    )
    logger.debug("donations")
    logger.debug("donations")
    logger.debug("donations")
    donations = await get_donation(donations_id)
    logger.debug(donations)
    assert donations, "Newly created donations couldn't be retrieved"
    return donations


async def get_donation(donations_id: str) -> Optional[Donations]:
    row = await db.fetchone("SELECT * FROM donations.donations WHERE id = ?", (donations_id,))
    return Donations(**row) if row else None


async def get_donations(wallet_ids: Union[str, List[str]]) -> List[Donations]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM donations.donations WHERE wallet IN ({q})", (*wallet_ids,)
    )

    return [Donations(**row) for row in rows]


async def delete_donations(donations_id: str) -> None:
    await db.execute("DELETE FROM donations.donations WHERE id = ?", (donations_id,))
