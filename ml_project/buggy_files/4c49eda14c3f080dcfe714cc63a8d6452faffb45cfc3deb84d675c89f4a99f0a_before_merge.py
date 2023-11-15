    def perform_request(self, endpoint, read_callback, data="", method='GET', capture_errors=True):
        """
        Perform a HTTP request.
        :param endpoint: the endpoint to call (i.e. "statistics")
        :param read_callback: the callback to be called with result info when we have the data
        :param data: optional POST data to be sent with the request
        :param method: the HTTP verb (GET/POST/PUT/PATCH)
        :param capture_errors: whether errors should be handled by this class (defaults to True)
        """
        performed_requests[self.request_id] = [endpoint, method, data, time(), -1]
        performed_requests_ids.append(self.request_id)
        if len(performed_requests_ids) > 200:
            del performed_requests[performed_requests_ids.pop(0)]
        url = self.base_url + endpoint

        if method == 'GET':
            buf = QBuffer()
            buf.setData(data)
            buf.open(QIODevice.ReadOnly)
            get_request = QNetworkRequest(QUrl(url))
            self.reply = self.sendCustomRequest(get_request, "GET", buf)
            buf.setParent(self.reply)
        elif method == 'PATCH':
            buf = QBuffer()
            buf.setData(data)
            buf.open(QIODevice.ReadOnly)
            patch_request = QNetworkRequest(QUrl(url))
            self.reply = self.sendCustomRequest(patch_request, "PATCH", buf)
            buf.setParent(self.reply)
        elif method == 'PUT':
            request = QNetworkRequest(QUrl(url))
            request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
            self.reply = self.put(request, data)
        elif method == 'DELETE':
            buf = QBuffer()
            buf.setData(data)
            buf.open(QIODevice.ReadOnly)
            delete_request = QNetworkRequest(QUrl(url))
            self.reply = self.sendCustomRequest(delete_request, "DELETE", buf)
            buf.setParent(self.reply)
        elif method == 'POST':
            request = QNetworkRequest(QUrl(url))
            request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
            self.reply = self.post(request, data)

        if read_callback:
            self.received_json.connect(read_callback)

        self.finished.connect(lambda reply: self.on_finished(reply, capture_errors))