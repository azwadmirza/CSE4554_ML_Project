    def notify_of_subprocess(self, conn):
        with self.session:
            if self.start_request is None or conn in self._known_subprocesses:
                return
            if "processId" in self.start_request.arguments:
                log.warning(
                    "Not reporting subprocess for {0}, because the parent process "
                    'was attached to using "processId" rather than "port".',
                    self.session,
                )
                return

            log.info("Notifying {0} about {1}.", self, conn)
            body = dict(self.start_request.arguments)
            self._known_subprocesses.add(conn)

        body["name"] = fmt("Subprocess {0}", conn.pid)
        body["request"] = "attach"
        if "host" not in body:
            body["host"] = "127.0.0.1"
        if "port" not in body:
            _, body["port"] = self.listener.getsockname()
        if "processId" in body:
            del body["processId"]
        body["subProcessId"] = conn.pid

        self.channel.send_event("debugpyAttach", body)