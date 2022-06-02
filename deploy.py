import time
import ray
from ray import serve


@serve.deployment(
    _autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 10,
        "target_num_ongoing_requests_per_replica": 1,
        "upscale_delay_s": 2,
    },
    version="v1",
    max_concurrent_queries=10,
)
class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self, request):
        self.count += 1
        time.sleep(1)
        return {"count": self.count}


ray.init(address="ray://localhost:10001", namespace="serve")
serve.start(detached=True)


def deploy(deployment_name: str):
    try:
        serve.get_deployment(deployment_name).delete()
    except:
        pass
    Counter.options(name=deployment_name, ray_actor_options={"num_cpus": 0.4}).deploy()  # type: ignore
