import asyncio
import time

import requests


async def fetch(user_id):
    time.sleep(1)
    return requests.get(f"/users/{user_id}")


async def safe(client, user_id):
    response = await client.get(f"/users/{user_id}", timeout=5.0)
    response.raise_for_status()
    return response.json()


def helper():
    time.sleep(1)


async def main():
    return await safe(None, "u1")
