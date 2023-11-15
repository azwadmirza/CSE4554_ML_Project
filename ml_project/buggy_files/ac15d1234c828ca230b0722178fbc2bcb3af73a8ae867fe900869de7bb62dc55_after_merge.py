        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._heartbeat_timeout = heartbeat_timeout
            if self._heartbeat_timeout > 0:
                self._heartbeat = threading.Event()
                self._heartbeat_thread = threading.Thread(
                    target=self._check_heartbeat,
                    args=(os.getpid(),),
                    daemon=True,
                )
                self._heartbeat_thread.start()
            else:
                self._heartbeat = None