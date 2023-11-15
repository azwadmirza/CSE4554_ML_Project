    def _handle_response_error(self, err):
        # If an error gets to this point, log it and kill the connection.
        if err.check(DownloadCanceledError, RequestCanceledError, error.ConnectionAborted):
            # TODO: (wish-list) it seems silly to close the connection over this, and it shouldn't
            # TODO: always be this way. it's done this way now because the client has no other way
            # TODO: of telling the server it wants the download to stop. It would be great if the
            # TODO: protocol had such a mechanism.
            log.info("Closing the connection to %s because the download of blob %s was canceled",
                     self.peer, self._blob_download_request.blob)
            result = None
        elif not err.check(MisbehavingPeerError, ConnectionClosedBeforeResponseError):
            log.warning("The connection to %s is closing due to: %s", self.peer, err)
            result = err
        else:
            log.error("The connection to %s is closing due to an unexpected error: %s",
                      self.peer, err)
            result = err

        self.transport.loseConnection()
        return result