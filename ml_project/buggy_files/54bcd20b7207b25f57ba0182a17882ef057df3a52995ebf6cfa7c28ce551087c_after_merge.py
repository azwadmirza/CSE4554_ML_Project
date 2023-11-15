    def submit(self, batch: jaeger.Batch):
        """Submits batches to Thrift HTTP Server through Binary Protocol.

        Args:
            batch: Object to emit Jaeger spans.
        """
        batch.write(self.protocol)
        self.http_transport.flush()
        code = self.http_transport.code
        msg = self.http_transport.message
        if code >= 300 or code < 200:
            logger.error(
                "Traces cannot be uploaded; HTTP status code: %s, message: %s",
                code,
                msg,
            )