    def replay_request(self, f, block=False, run_scripthooks=True):
        """
            Returns None if successful, or error message if not.
        """
        if f.live and run_scripthooks:
            return "Can't replay live request."
        if f.intercepted:
            return "Can't replay while intercepting..."
        if f.request.content is None:
            return "Can't replay request with missing content..."
        if f.request:
            f.backup()
            f.request.is_replay = True
            if "Content-Length" in f.request.headers:
                f.request.headers["Content-Length"] = str(len(f.request.content))
            f.response = None
            f.error = None
            self.process_new_request(f)
            rt = RequestReplayThread(
                self.server.config,
                f,
                self.masterq if run_scripthooks else False,
                self.should_exit
            )
            rt.start()  # pragma: no cover
            if block:
                rt.join()