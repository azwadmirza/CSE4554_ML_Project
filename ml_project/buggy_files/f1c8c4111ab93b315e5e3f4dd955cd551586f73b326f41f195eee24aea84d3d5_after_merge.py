    def _check_failure_status(self) -> None:
        """ Check the status of command failures. Raise exceptions as necessary

        The failure status property is used by the various asynchronous
        command execution threads which interface with the
        remote browser manager processes. If a failure status is found, the
        appropriate steps are taken to gracefully close the infrastructure
        """
        self.logger.debug("Checking command failure status indicator...")
        if not self.failure_status:
            return

        self.logger.debug(
            "TaskManager failure status set, halting command execution.")
        self._shutdown_manager()
        if self.failure_status['ErrorType'] == 'ExceedCommandFailureLimit':
            raise CommandExecutionError(
                "TaskManager exceeded maximum consecutive command "
                "execution failures.",
                self.failure_status['CommandSequence']
            )
        elif (self.failure_status['ErrorType'] == ("ExceedLaunch"
                                                   "FailureLimit")):
            raise CommandExecutionError(
                "TaskManager failed to launch browser within allowable "
                "failure limit.", self.failure_status['CommandSequence']
            )
        if self.failure_status['ErrorType'] == 'CriticalChildException':
            exc_type, exc, tb = pickle.loads(self.failure_status['Exception'])
            raise exc.with_traceback(tb)