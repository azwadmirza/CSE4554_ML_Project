    def _issue_command(self, browser, command_sequence, condition=None):
        """
        sends command tuple to the BrowserManager
        """
        browser.is_fresh = False

        # if this is a synced call, block on condition
        if condition is not None:
            with condition:
                condition.wait()

        reset = command_sequence.reset
        if not reset:
            self.logger.warn(
                "BROWSER %i: Browser will not reset after CommandSequence "
                "executes. OpenWPM does not currently support stateful crawls "
                "(see: https://github.com/mozilla/OpenWPM/projects/2). "
                "The next command issued to this browser may or may not "
                "use the same profile (depending on the failure status of "
                "this command). To prevent this warning, initialize the "
                "CommandSequence with `reset` set to `True` to use a fresh "
                "profile for each command." % browser.crawl_id
            )
        start_time = None
        for command_and_timeout in command_sequence.commands_with_timeout:
            command, timeout = command_and_timeout
            if command[0] in ['GET', 'BROWSE',
                              'SAVE_SCREENSHOT',
                              'SCREENSHOT_FULL_PAGE',
                              'DUMP_PAGE_SOURCE',
                              'RECURSIVE_DUMP_PAGE_SOURCE']:
                start_time = time.time()
                command += (browser.curr_visit_id,)
            elif command[0] in ['DUMP_FLASH_COOKIES', 'DUMP_PROFILE_COOKIES']:
                command += (start_time, browser.curr_visit_id,)
            browser.current_timeout = timeout
            # passes off command and waits for a success (or failure signal)
            browser.command_queue.put(command)
            command_arguments = command[1] if len(command) > 1 else None

            # received reply from BrowserManager, either success or failure
            critical_failure = False
            error_text = None
            tb = None
            try:
                status = browser.status_queue.get(
                    True, browser.current_timeout)
                if status == "OK":
                    command_status = 'ok'
                elif status[0] == "CRITICAL":
                    self.logger.critical(
                        "BROWSER %i: Received critical error from browser "
                        "process while executing command %s. Setting failure "
                        "status." % (browser.crawl_id, str(command)))
                    self.failure_status = {
                        'ErrorType': 'CriticalChildException',
                        'CommandSequence': command_sequence,
                        'Exception': status[1]
                    }
                    error_text, tb = self._unpack_picked_error(status[1])
                    critical_failure = True
                elif status[0] == "FAILED":
                    command_status = 'error'
                    error_text, tb = self._unpack_picked_error(status[1])
                    self.logger.info(
                        "BROWSER %i: Received failure status while executing "
                        "command: %s" % (browser.crawl_id, command[0]))
                elif status[0] == 'NETERROR':
                    command_status = 'neterror'
                    error_text, tb = self._unpack_picked_error(status[1])
                    error_text = parse_neterror(error_text)
                    self.logger.info(
                        "BROWSER %i: Received neterror %s while executing "
                        "command: %s" %
                        (browser.crawl_id, error_text, command[0])
                    )
                else:
                    raise ValueError(
                        "Unknown browser status message %s" % status
                    )
            except EmptyQueue:
                command_status = 'timeout'
                self.logger.info(
                    "BROWSER %i: Timeout while executing command, %s, killing "
                    "browser manager" % (browser.crawl_id, command[0]))

            self.sock.send(("crawl_history", {
                "crawl_id": browser.crawl_id,
                "visit_id": browser.curr_visit_id,
                "command": command[0],
                "arguments": str(command_arguments),
                "retry_number": command_sequence.retry_number,
                "command_status": command_status,
                "error": error_text,
                "traceback": tb
            }))

            if critical_failure:
                return

            if command_status != 'ok':
                with self.threadlock:
                    self.failurecount += 1
                if self.failurecount > self.failure_limit:
                    self.logger.critical(
                        "BROWSER %i: Command execution failure pushes failure "
                        "count above the allowable limit. Setting "
                        "failure_status." % browser.crawl_id)
                    self.failure_status = {
                        'ErrorType': 'ExceedCommandFailureLimit',
                        'CommandSequence': command_sequence
                    }
                    return
                browser.restart_required = True
                self.logger.debug("BROWSER %i: Browser restart required" % (
                    browser.crawl_id))
            else:
                with self.threadlock:
                    self.failurecount = 0

            if browser.restart_required:
                break

        # Sleep after executing CommandSequence to provide extra time for
        # internal buffers to drain. Stopgap in support of #135
        time.sleep(2)

        if self.closing:
            return

        if browser.restart_required or reset:
            success = browser.restart_browser_manager(clear_profile=reset)
            if not success:
                self.logger.critical(
                    "BROWSER %i: Exceeded the maximum allowable consecutive "
                    "browser launch failures. Setting failure_status." % (
                        browser.crawl_id))
                self.failure_status = {
                    'ErrorType': 'ExceedLaunchFailureLimit',
                    'CommandSequence': command_sequence
                }
                return
            browser.restart_required = False