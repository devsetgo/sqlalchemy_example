import time
from httpx import AsyncClient, Timeout
from tqdm import tqdm
import asyncio
import secrets

CONCURRENT_REQUEST_LIMIT = 2000  # Limit to prevent PoolTimeout, adjust as needed
REQUEST_TIMEOUT = 10.0  # Time to wait for server to respond, adjust as needed


async def run(n):
    semaphore = asyncio.Semaphore(
        CONCURRENT_REQUEST_LIMIT
    )  # Limit the number of concurrent requests

    timeout = Timeout(REQUEST_TIMEOUT)  # Set request timeout
    async with AsyncClient(timeout=timeout) as client:
        tasks = []
        for i in tqdm(range(n)):
            data = {"name": f"user-{i}-{secrets.token_hex(4)}"}
            task = send_request(
                client, semaphore, "http://localhost:5000/users/", json=data
            )
            tasks.append(task)

        resp = await asyncio.gather(*tasks)

        return resp


async def send_request(client, semaphore, *args, **kwargs):
    async with semaphore:  # Only allow a certain number of requests to be sent at once
        return await client.post(*args, **kwargs)


if __name__ == "__main__":
    n = 1000  # replace with the number of posts you want to make
    start_time = time.time()
    responses = asyncio.run(run(n))
    end_time = time.time()
    elapsed_time = end_time - start_time
    requests_per_second = n / elapsed_time
    print(f"Elapsed time: {format(elapsed_time, '.2f')} seconds")  # Limit to 2 decimal places
    print(f"Requests per second: {format(requests_per_second, '.2f')}")  # Limit to 2 decimal places
