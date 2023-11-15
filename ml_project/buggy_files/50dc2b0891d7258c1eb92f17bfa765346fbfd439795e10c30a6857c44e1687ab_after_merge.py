    def _log_main(self) -> None:
        stub = ray_client_pb2_grpc.RayletLogStreamerStub(self.channel)
        log_stream = stub.Logstream(
            iter(self.request_queue.get, None), metadata=self._metadata)
        try:
            for record in log_stream:
                if record.level < 0:
                    self.stdstream(level=record.level, msg=record.msg)
                self.log(level=record.level, msg=record.msg)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                # Graceful shutdown. We've cancelled our own connection.
                logger.info("Cancelling logs channel")
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                # TODO(barakmich): The server may have
                # dropped. In theory, we can retry, as per
                # https://grpc.github.io/grpc/core/md_doc_statuscodes.html but
                # in practice we may need to think about the correct semantics
                # here.
                logger.info("Server disconnected from logs channel")
            else:
                # Some other, unhandled, gRPC error
                logger.error(
                    f"Got Error from logger channel -- shutting down: {e}")
                raise e