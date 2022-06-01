import asyncio
from deploy import deploy
from query import send_request

DEPLOYMENT_NAME = "test_deployment"

if __name__ == "__main__":
    deploy(deployment_name=DEPLOYMENT_NAME)

    loop = asyncio.get_event_loop()
    tasks = []
    for i in range(1000):
        for j in range(10):
            tasks.append(loop.create_task(deployment_name=DEPLOYMENT_NAME))
        loop.run_until_complete(asyncio.wait(tasks))
        tasks = []
    loop.close()
