from .base import base_value
from ..service.pricing import pricing_value


def order_value():
    return base_value() + pricing_value()
