    def perform_request(self, endpoint, read_callback, data="", method='GET', capture_errors=True,
                        priority=QueuePriorityEnum.CRITICAL, on_cancel=lambda: None):
        """
        Perform a HTTP request.
        :param endpoint: the endpoint to call (i.e. "statistics")
        :param read_callback: the callback to be called with result info when we have the data
        :param data: optional POST data to be sent with the request
        :param method: the HTTP verb (GET/POST/PUT/PATCH)
        :param capture_errors: whether errors should be handled by this class (defaults to True)
        """
        url = self.base_url + endpoint

        self.status_code = -1
        self.on_cancel = on_cancel
        request_queue.enqueue(self,
                              lambda: self.dispatch_map.get(method, lambda x, y, z: None)(endpoint, data, url),
                              priority)

        if read_callback:
            self.received_json.connect(read_callback)

        self.finished.connect(lambda reply: self.on_finished(reply, capture_errors))