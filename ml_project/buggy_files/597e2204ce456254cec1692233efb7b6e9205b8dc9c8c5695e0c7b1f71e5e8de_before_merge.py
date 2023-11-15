    def _blocking_send(self, req: ray_client_pb2.DataRequest
                       ) -> ray_client_pb2.DataResponse:
        req_id = self._next_id()
        req.req_id = req_id
        self.request_queue.put(req)
        data = None
        with self.cv:
            self.cv.wait_for(lambda: req_id in self.ready_data)
            data = self.ready_data[req_id]
            del self.ready_data[req_id]
        return data