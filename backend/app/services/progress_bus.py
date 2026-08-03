import asyncio
from collections import defaultdict


class ProgressBus:
    """In-memory pub/sub so the SSE endpoint can stream job progress without
    polling the database on every tick. Single-process only — fine for a
    local desktop-style app; would move to Redis pub/sub for a multi-worker
    deployment."""

    def __init__(self):
        self._subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def subscribe(self, job_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers[job_id].append(queue)
        return queue

    def unsubscribe(self, job_id: str, queue: asyncio.Queue) -> None:
        if queue in self._subscribers.get(job_id, []):
            self._subscribers[job_id].remove(queue)

    async def publish(self, job_id: str, event: dict) -> None:
        for queue in list(self._subscribers.get(job_id, [])):
            await queue.put(event)


progress_bus = ProgressBus()
