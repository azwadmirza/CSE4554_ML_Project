    def __init__(self, run=True):

        self.client = MaestralApiClient()

        # periodically check for updates and refresh account info
        self.update_thread = Thread(
            name="Maestral update check",
            target=self._periodic_refresh,
            daemon=True,
        )
        self.update_thread.start()

        # monitor needs to be created before any decorators are called
        self.monitor = MaestralMonitor(self.client)
        self.sync = self.monitor.sync

        if NOTIFY_SOCKET and system_notifier:
            # notify systemd that we have successfully started
            system_notifier.notify("READY=1")

        if WATCHDOG_USEC and int(WATCHDOG_PID) == os.getpid() and system_notifier:
            # notify systemd periodically that we are still alive
            self.watchdog_thread = Thread(
                name="Maestral watchdog",
                target=self._periodic_watchdog,
                daemon=True,
            )
            self.update_thread.start()

        if run:
            # if `run == False`, make sure that you manually run the setup
            # before calling `start_sync`
            if self.pending_dropbox_folder():
                self.create_dropbox_directory()
                self.set_excluded_folders()

                self.sync.last_cursor = ""
                self.sync.last_sync = 0

            self.start_sync()