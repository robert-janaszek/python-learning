import asyncio
import time

from python_week1.timer import Timer


async def fetch_metrics(service_id: int) -> dict:
    await asyncio.sleep(0.5)
    return {"service_id": service_id}


def fetch_metrics_sync(service_id: int) -> dict:
    time.sleep(2)
    return {"service_id": service_id}


async def fetch_all() -> None:
    workers = asyncio.Semaphore(3)

    with Timer("fetching services"):

        async def fetch_one(item: int) -> dict:
            async with workers:
                if item == 3:
                    return await asyncio.to_thread(fetch_metrics_sync, item)
                    # return fetch_metrics_sync(item)
                return await fetch_metrics(item)

        ready = await asyncio.gather(*(fetch_one(item + 1) for item in range(20)))
        print(ready)
