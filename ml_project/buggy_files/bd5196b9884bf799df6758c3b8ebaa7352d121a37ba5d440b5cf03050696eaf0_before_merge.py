    def check_resources(self):
        """
        Check CPU and memory usage.
        """
        self._logger.debug("Checking memory/CPU usage")
        if len(self.cpu_data) == self.history_size:
            self.cpu_data.pop(0)
        if len(self.memory_data) == self.history_size:
            self.memory_data.pop(0)

        time_seconds = time.time()
        self.cpu_data.append((time_seconds, self.process.cpu_percent(interval=None)))

        # Get the memory usage of the process
        # psutil package 4.0.0 introduced memory_full_info() method which among other info also returns uss.
        # uss (Unique Set Size) is probably the most representative metric for determining how much memory is
        # actually being used by a process.
        # However, on psutil version < 4.0.0, we fallback to use rss (Resident Set Size) which is the non-swapped
        # physical memory a process has used
        if hasattr(self.process, "memory_full_info") and callable(getattr(self.process, "memory_full_info")):
            self.memory_data.append((time_seconds, self.process.memory_full_info().uss))
        elif hasattr(self.process, "memory_info") and callable(getattr(self.process, "memory_info")):
            self.memory_data.append((time_seconds, self.process.memory_info().rss))