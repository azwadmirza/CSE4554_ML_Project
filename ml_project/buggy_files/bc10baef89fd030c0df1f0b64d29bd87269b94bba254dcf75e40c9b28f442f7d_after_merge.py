    def _on_reply_error(self, code):
        """Handle QNetworkReply errors."""
        if code == QNetworkReply.OperationCanceledError:
            return

        if self._reply is None:
            error = "Unknown error: {}".format(
                debug.qenum_key(QNetworkReply, code))
        else:
            error = self._reply.errorString()

        self._die(error)