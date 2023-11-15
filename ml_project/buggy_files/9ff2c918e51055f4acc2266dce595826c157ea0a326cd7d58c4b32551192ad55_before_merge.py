    def _timed_queue_join(self, timeout):
        # type: (float) -> bool
        deadline = time() + timeout
        queue = self._queue
        queue.all_tasks_done.acquire()  # type: ignore
        try:
            while queue.unfinished_tasks:  # type: ignore
                delay = deadline - time()
                if delay <= 0:
                    return False
                queue.all_tasks_done.wait(timeout=delay)  # type: ignore
            return True
        finally:
            queue.all_tasks_done.release()  # type: ignore