    def _get(self, ref: ClientObjectRef, timeout: float):
        req = ray_client_pb2.GetRequest(id=ref.id, timeout=timeout)
        try:
            data = self.data_client.GetObject(req)
        except grpc.RpcError as e:
            raise e.details()
        if not data.valid:
            try:
                err = cloudpickle.loads(data.error)
            except pickle.UnpicklingError:
                logger.exception("Failed to deserialize {}".format(data.error))
                raise
            logger.error(err)
            raise err
        return loads_from_server(data.data)