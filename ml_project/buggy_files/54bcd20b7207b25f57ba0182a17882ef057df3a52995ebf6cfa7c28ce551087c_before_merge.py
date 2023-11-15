    def submit(self, batch: jaeger.Batch):
        """Submits batches to Thrift HTTP Server through Binary Protocol.

        Args:
            batch: Object to emit Jaeger spans.
        """
        try:
            self.client.submitBatches([batch])
            # it will call http_transport.flush() and
            # status code and message will be updated
            code = self.http_transport.code
            msg = self.http_transport.message
            if code >= 300 or code < 200:
                logger.error(
                    "Traces cannot be uploaded; HTTP status code: %s, message %s",
                    code,
                    msg,
                )
        finally:
            if self.http_transport.isOpen():
                self.http_transport.close()