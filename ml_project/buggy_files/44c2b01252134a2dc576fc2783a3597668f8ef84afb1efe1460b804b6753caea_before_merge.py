    def shutdown(self):
        self.workflow_scheduling_manager.shutdown()
        self.job_manager.shutdown()
        self.object_store.shutdown()
        if self.heartbeat:
            self.heartbeat.shutdown()
        self.update_repository_manager.shutdown()
        try:
            self.control_worker.shutdown()
        except AttributeError:
            # There is no control_worker
            pass