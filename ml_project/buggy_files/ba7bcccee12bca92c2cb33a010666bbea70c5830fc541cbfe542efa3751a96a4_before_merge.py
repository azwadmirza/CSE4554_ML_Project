    def replay_request(self, f, block=False):
        """
            Returns an http_replay.RequestReplayThred object.
            May raise exceptions.ReplayError.
        """
        if f.live:
            raise exceptions.ReplayError(
                "Can't replay live flow."
            )
        if f.intercepted:
            raise exceptions.ReplayError(
                "Can't replay intercepted flow."
            )
        if f.request.raw_content is None:
            raise exceptions.ReplayError(
                "Can't replay flow with missing content."
            )
        if not f.request:
            raise exceptions.ReplayError(
                "Can't replay flow with missing request."
            )

        f.backup()
        f.request.is_replay = True

        # TODO: We should be able to remove this.
        if "Content-Length" in f.request.headers:
            f.request.headers["Content-Length"] = str(len(f.request.raw_content))

        f.response = None
        f.error = None
        # FIXME: process through all addons?
        # self.process_new_request(f)
        rt = http_replay.RequestReplayThread(
            self.server.config,
            f,
            self.event_queue,
            self.should_exit
        )
        rt.start()  # pragma: no cover
        if block:
            rt.join()
        return rt