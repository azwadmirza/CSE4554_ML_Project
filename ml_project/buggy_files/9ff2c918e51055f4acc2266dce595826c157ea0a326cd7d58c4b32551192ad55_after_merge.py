    def _timed_queue_join(self, timeout):
        # type: (float) -> bool
        deadline = time() + timeout
        queue = self._queue

        real_all_tasks_done = getattr(
            queue, "all_tasks_done", None
        )  # type: Optional[Any]
        if real_all_tasks_done is not None:
            real_all_tasks_done.acquire()
            all_tasks_done = real_all_tasks_done  # type: Optional[Any]
        elif queue.__module__.startswith("eventlet."):
            all_tasks_done = getattr(queue, "_cond", None)
        else:
            all_tasks_done = None

        try:
            while queue.unfinished_tasks:  # type: ignore
                delay = deadline - time()
                if delay <= 0:
                    return False
                if all_tasks_done is not None:
                    all_tasks_done.wait(timeout=delay)
                else:
                    # worst case, we just poll the number of remaining tasks
                    sleep(0.1)

            return True
        finally:
            if real_all_tasks_done is not None:
                real_all_tasks_done.release()  # type: ignore