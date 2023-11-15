    def push(self):
        """
        Pushes this context on the current CPU Thread.
        """
        driver.cuCtxPushCurrent(self.handle)
        # setup *deallocations* as the context becomes active for the first time
        if self.deallocations is None:
            self.deallocations = _PendingDeallocs(self.get_memory_info().total)