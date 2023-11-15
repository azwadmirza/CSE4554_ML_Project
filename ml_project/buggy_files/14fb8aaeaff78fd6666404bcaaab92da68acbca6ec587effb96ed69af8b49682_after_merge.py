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
            with self.cv:
                self._in_shutdown = True
                self.cv.notify_all()
            if e.code() == grpc.StatusCode.CANCELLED:
                # Gracefully shutting down
                logger.info("Cancelling data channel")
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                # TODO(barakmich): The server may have
                # dropped. In theory, we can retry, as per
                # https://grpc.github.io/grpc/core/md_doc_statuscodes.html but
                # in practice we may need to think about the correct semantics
                # here.
                logger.info("Server disconnected from data channel")
            else:
                logger.error(
                    f"Got Error from data channel -- shutting down: {e}")
                raise e