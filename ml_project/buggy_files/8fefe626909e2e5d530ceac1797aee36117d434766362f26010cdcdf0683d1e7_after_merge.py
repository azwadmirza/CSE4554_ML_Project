    def execute_command(self, options):
        """
        Handles the 'execute' CLI command.

        If there is already a task queue running in this process, adds the execution to the queue.
        If FlexGet is being invoked with this command, starts up a task queue and runs the execution.

        Fires events:

        * manager.execute.started
        * manager.execute.completed

        :param options: argparse options
        """
        fire_event('manager.execute.started', self, options)
        if self.task_queue.is_alive() or self.is_daemon:
            if not self.task_queue.is_alive():
                log.error('Task queue has died unexpectedly. Restarting it. Please open an issue on Github and include'
                          ' any previous error logs.')
                self.task_queue = TaskQueue()
                self.task_queue.start()
            if len(self.task_queue):
                log.verbose('There is a task already running, execution queued.')
            finished_events = self.execute(options, output=logger.get_capture_stream(),
                                           loglevel=logger.get_capture_loglevel())
            if not options.cron:
                # Wait until execution of all tasks has finished
                for _, _, event in finished_events:
                    event.wait()
        else:
            self.task_queue.start()
            self.ipc_server.start()
            self.execute(options)
            self.shutdown(finish_queue=True)
            self.task_queue.wait()
        fire_event('manager.execute.completed', self, options)