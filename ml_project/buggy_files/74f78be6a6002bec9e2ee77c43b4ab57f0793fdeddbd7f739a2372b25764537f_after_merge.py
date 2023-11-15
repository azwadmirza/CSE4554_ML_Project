    def __reconcile(self, driver):
        """
        Queries the master about a list of running tasks. If the master has no knowledge of them, their state will be
        updated to LOST.
        """
        # FIXME: we need additional reconciliation. What about the tasks the master knows about but haven't updated?
        now = time.time()
        if now > self.lastReconciliation + self.reconciliationPeriod:
            self.lastReconciliation = now
            driver.reconcileTasks(self.runningJobMap.keys())