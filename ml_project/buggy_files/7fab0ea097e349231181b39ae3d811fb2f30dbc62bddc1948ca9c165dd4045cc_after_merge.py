    def _handle_response_error(self, err):
        # If an error gets to this point, log it and kill the connection.
        if err.check(DownloadCanceledError, RequestCanceledError, error.ConnectionAborted,
                     ConnectionClosedBeforeResponseError):
            # TODO: (wish-list) it seems silly to close the connection over this, and it shouldn't
            # TODO: always be this way. it's done this way now because the client has no other way
            # TODO: of telling the server it wants the download to stop. It would be great if the
            # TODO: protocol had such a mechanism.
            log.info("Closing the connection to %s because the download of blob %s was canceled",
                     self.peer, self._blob_download_request.blob)
            result = None
        elif err.check(MisbehavingPeerError):
            log.warning("The connection to %s is closing due to: %s", self.peer, err)
            result = err
        else:
            log.error("The connection to %s is closing due to an unexpected error: %s",
                      self.peer, err)
            result = err
        self._blob_download_request = None
        self._downloading_blob = False
        self.transport.loseConnection()
        return result