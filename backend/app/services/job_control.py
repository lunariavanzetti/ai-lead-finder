import asyncio


class JobControlEntry:
    def __init__(self):
        self.paused_event = asyncio.Event()
        self.paused_event.set()  # set == not paused (runnable)
        self.cancelled = False


class JobControlRegistry:
    def __init__(self):
        self._jobs: dict[str, JobControlEntry] = {}

    def register(self, job_id: str) -> JobControlEntry:
        entry = JobControlEntry()
        self._jobs[job_id] = entry
        return entry

    def get(self, job_id: str) -> JobControlEntry | None:
        return self._jobs.get(job_id)

    def pause(self, job_id: str) -> bool:
        entry = self._jobs.get(job_id)
        if not entry:
            return False
        entry.paused_event.clear()
        return True

    def resume(self, job_id: str) -> bool:
        entry = self._jobs.get(job_id)
        if not entry:
            return False
        entry.paused_event.set()
        return True

    def cancel(self, job_id: str) -> bool:
        entry = self._jobs.get(job_id)
        if not entry:
            return False
        entry.cancelled = True
        entry.paused_event.set()  # unblock a paused loop so it can observe the cancellation
        return True

    async def wait_if_paused(self, job_id: str) -> None:
        entry = self._jobs.get(job_id)
        if entry:
            await entry.paused_event.wait()

    def is_cancelled(self, job_id: str) -> bool:
        entry = self._jobs.get(job_id)
        return bool(entry and entry.cancelled)

    def cleanup(self, job_id: str) -> None:
        self._jobs.pop(job_id, None)


job_control = JobControlRegistry()
