from sqlite3 import Row
from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class Donations(BaseModel):
    id: str = Query(None)
    title: str
    wallet: str = Query(None)
    description: str = Query(None)