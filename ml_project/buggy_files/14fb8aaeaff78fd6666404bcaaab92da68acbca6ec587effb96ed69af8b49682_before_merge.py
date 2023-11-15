    def _data_main(self) -> None:
        stub = ray_client_pb2_grpc.RayletDataStreamerStub(self.channel)
        resp_stream = stub.Datapath(
            iter(self.request_queue.get, None),
            metadata=[("client_id", self._client_id)] + self._metadata,
            wait_for_ready=True)
        try:
            for response in resp_stream:
                if response.req_id == 0:
                    # This is not being waited for.
                    logger.debug(f"Got unawaited response {response}")
                    continue
                with self.cv:
                    self.ready_data[response.req_id] = response
                    self.cv.notify_all()
        except grpc.RpcError as e:
            if grpc.StatusCode.CANCELLED == e.code():
                # Gracefully shutting down
                logger.info("Cancelling data channel")
            else:
                logger.error(
                    f"Got Error from data channel -- shutting down: {e}")
                raise e