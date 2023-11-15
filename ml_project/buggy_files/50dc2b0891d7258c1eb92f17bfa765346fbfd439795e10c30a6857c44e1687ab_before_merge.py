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
            if grpc.StatusCode.CANCELLED != e.code():
                # Not just shutting down normally
                logger.error(
                    f"Got Error from logger channel -- shutting down: {e}")
                raise e