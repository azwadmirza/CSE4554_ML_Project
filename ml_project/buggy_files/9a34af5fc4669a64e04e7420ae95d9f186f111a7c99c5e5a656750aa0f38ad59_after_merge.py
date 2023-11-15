    def stop(self, halt_reactor: bool = False) -> None:
        """Stop services"""
        self._availability_tracker.stop()
        if self._learning_task.running:
            self.stop_learning_loop()
        if not self.federated_only:
            self.work_tracker.stop()
        if self._arrangement_pruning_task.running:
            self._arrangement_pruning_task.stop()
        if halt_reactor:
            reactor.stop()