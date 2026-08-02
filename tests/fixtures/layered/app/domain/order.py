from sqlalchemy.orm import Session
from httpx import AsyncClient


def total(order):
    return sum(item.price for item in order.items)
