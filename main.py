import asyncio
import time
import logging
import random
import ray
from ray import serve
from httpx import AsyncClient
from tqdm.asyncio import tarange, tqdm

RAY_CLIENT_SERVER_ADDRESS = "ray://localhost:10001"
RAY_SERVE_URL = "http://localhost:8000"
NUM_CLIENTS = 10
MAX_NUM_REQUESTS = 1000
MAX_REPLICAS = 20
MAX_ONGOING = 1
REQUEST_SLEEP = 0.05
DEPLOYMENT_NAME = "test_deployment"


@serve.deployment(
    _autoscaling_config={
        "min_replicas": 1,
        "max_replicas": MAX_REPLICAS,
        "target_num_ongoing_requests_per_replica": MAX_ONGOING,
        "upscale_delay_s": 5,
        "downscale_delay_s": 15,
        "look_back_period_s": 5,
        "metrics_interval_s": 1,
    },
    version="v1",
    max_concurrent_queries=MAX_ONGOING*2,
)
class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self, request):
        self.count += 1
        time.sleep(REQUEST_SLEEP)
        return {"count": self.count}


def deploy(deployment_name):
    try:
        serve.get_deployment(deployment_name).delete()
    except:
        pass
    Counter.options(name=deployment_name, ray_actor_options={"num_cpus": 0.4}).deploy()


async def send_requests(deployment_name, tbar):
    for i in tbar:
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{RAY_SERVE_URL}/{deployment_name}",
                    timeout=30,
                )
                response.raise_for_status()
            except Exception as e:
                logging.exception(e)
    tbar.close()


async def main():
    tbars = []
    tasks = []
    for i in range(NUM_CLIENTS):
        num_requests = random.randint(MAX_NUM_REQUESTS/4, MAX_NUM_REQUESTS)
        tbars.append(tarange(num_requests, desc=f"Client #{i}", position=i+1, leave=False))
        tasks.append(
            loop.create_task(send_requests(deployment_name=DEPLOYMENT_NAME, tbar=tbars[i]))
        )
    await asyncio.wait(tasks)


async def monitor_replicas(deployment_name):
    replicas_bar = tqdm(position=0, total=MAX_REPLICAS, bar_format='Deployment replicas|{bar}|{n_fmt}/{total_fmt}')
    while True:
        replicas_bar.update(serve.get_deployment(deployment_name).num_replicas - replicas_bar.n)
        replicas_bar.refresh()
        await asyncio.sleep(1)


async def done():
    print("\n\nTest finished! Replicas will downscale, press Ctrl+C to exit...")
    await asyncio.sleep(30)


if __name__ == "__main__":
    ray.init(address=RAY_CLIENT_SERVER_ADDRESS, namespace="serve")
    serve.start(detached=True)
    deploy(DEPLOYMENT_NAME)
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_replicas(DEPLOYMENT_NAME))
    loop.run_until_complete(main())
    loop.run_until_complete(done())
    loop.stop()
