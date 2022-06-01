import asyncio
from deploy import deploy
from query import send_request

DEPLOYMENT_NAME = "test_deployment"

if __name__ == "__main__":
    deploy(deployment_name=DEPLOYMENT_NAME)

    loop = asyncio.get_event_loop()
    tasks = []
    for i in range(100):
        for j in range(100):
            tasks.append(
                loop.create_task(send_request(deployment_name=DEPLOYMENT_NAME))
            )
        loop.run_until_complete(asyncio.wait(tasks))
        print(f"Sent {i}% of the requests")
        tasks = []
    loop.close()
