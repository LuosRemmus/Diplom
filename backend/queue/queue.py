import asyncio
import random
from typing import Callable


async def producer(tasks: list, queue: asyncio.Queue):
    for task in tasks:
        await queue.put(task)


async def consumer(func: Callable, queue: asyncio.Queue, domain: str | None = None):
    while True:
        task = await queue.get()
        if domain:
            post_data = {
                "post_url": f"https://{domain}?w=wall{task.group_id}_{task.post_id}",
                "post_text": task.text,
                "comments": []
            }
            comments = await func(owner_id=task.group_id, post_id=task.post_id)

            for comment in comments:
                pass
        queue.task_done()


async def main():
    concurrency = 10
    tasks = [random.randint(10, 30) / 10 for i in range(30)]
    queue = asyncio.Queue(maxsize=concurrency * 10)

    for i in range(concurrency):
        asyncio.create_task(consumer(i, queue))

    await producer(tasks, queue)
    await queue.join()
    print('end')


if __name__ == '__main__':
    asyncio.run(main())
