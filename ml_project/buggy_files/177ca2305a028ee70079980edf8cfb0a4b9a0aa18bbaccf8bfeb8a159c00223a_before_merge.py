    def _request_failed(self, reason, request_type):
        if reason.check(DownloadCanceledError, RequestCanceledError, ConnectionAborted,
                        ConnectionClosedBeforeResponseError):
            return
        if reason.check(NoResponseError):
            self.requestor._incompatible_peers.append(self.peer)
        log.warning("A request of type '%s' failed. Reason: %s, Error type: %s",
                    request_type, reason.getErrorMessage(), reason.type)
        self.update_local_score(-10.0)
        if isinstance(reason, (InvalidResponseError, NoResponseError)):
            self.peer.update_score(-10.0)
        else:
            self.peer.update_score(-2.0)
        if reason.check(ConnectionClosedBeforeResponseError):
            return
        return reason