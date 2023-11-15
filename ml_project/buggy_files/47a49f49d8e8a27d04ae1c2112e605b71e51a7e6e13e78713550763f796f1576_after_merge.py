    def __monitor(self):
        to_monitor = self.workflow_scheduling_manager.active_workflow_schedulers
        while self.monitor_running:
            try:
                if self.invocation_grabber:
                    self.invocation_grabber.grab_unhandled_items()

                monitor_step_timer = self.app.execution_timer_factory.get_timer(
                    'internal.galaxy.workflows.scheduling_manager.monitor_step',
                    'Workflow scheduling manager monitor step complete.'
                )
                for workflow_scheduler_id, workflow_scheduler in to_monitor.items():
                    if not self.monitor_running:
                        return

                    self.__schedule(workflow_scheduler_id, workflow_scheduler)
                log.trace(monitor_step_timer.to_str())
            except Exception:
                log.exception('An exception occured scheduling while scheduling workflows')
            self._monitor_sleep(1)