    def _call_schedule_for_task(
            self, task: ray_client_pb2.ClientTask) -> List[bytes]:
        logger.debug("Scheduling %s" % task)
        task.client_id = self._client_id
        try:
            ticket = self.server.Schedule(task, metadata=self.metadata)
        except grpc.RpcError as e:
            raise decode_exception(e.details)
        if not ticket.valid:
            try:
                raise cloudpickle.loads(ticket.error)
            except Exception:
                logger.exception("Failed to deserialize {}".format(
                    ticket.error))
                raise
        return ticket.return_ids