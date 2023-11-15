    def run(self) -> None:
        self._create_pid_file()
        module_logger.info(
            "=== Starting... (loop runs every %ds) Hit ^C to stop", self.interval
        )
        loop = True
        loops = self._max_loops
        heartbeat = True
        while loop:
            try:
                if loops > 0:
                    loops -= 1
                    if loops == 0:
                        module_logger.warning(
                            "Ran out of loop counter, will stop after this one"
                        )
                        loop = False
                if self._need_hup or self._check_hup_file():
                    try:
                        module_logger.warning("Reloading configuration")
                        self._load_config()
                        self.hup_loggers()
                        self._need_hup = False
                    except Exception:
                        module_logger.exception("Error while reloading configuration")
                        sys.exit(1)
                self.run_loop()

                if (
                    module_logger.level in ["error", "critical", "warn"]
                    and self.heartbeat
                ):
                    heartbeat = not heartbeat
                    if heartbeat:
                        sys.stdout.write(".")
                        sys.stdout.flush()
            except KeyboardInterrupt:
                module_logger.info("Received ^C")
                loop = False
            except Exception:
                module_logger.exception("Caught unhandled exception during main loop")
            if loop and self._network:
                if (
                    self._remote_listening_thread
                    and not self._remote_listening_thread.is_alive()
                ):
                    module_logger.error("Listener thread died :(")
                    self._start_network_thread()
            if self.one_shot:
                break

            try:
                if loop:
                    time.sleep(self.interval)
            except Exception:
                module_logger.info("Quitting")
                loop = False

        self._remove_pid_file()