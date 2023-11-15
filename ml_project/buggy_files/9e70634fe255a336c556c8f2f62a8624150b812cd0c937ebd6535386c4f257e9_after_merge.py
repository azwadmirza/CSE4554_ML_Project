    def forward_request(self, method, path, data, headers):
        if method == 'OPTIONS':
            return 200

        req_data = self.parse_request_data(method, path, data)

        if req_data:
            action = req_data.get('Action', [None])[0]
            if action == 'SendMessage':
                new_response = self._send_message(path, data, req_data, headers)
                if new_response:
                    return new_response
            elif action == 'SetQueueAttributes':
                self._set_queue_attributes(path, req_data, headers)

            if 'QueueName' in req_data:
                encoded_data = urlencode(req_data, doseq=True) if method == 'POST' else ''
                modified_url = None
                if method == 'GET':
                    base_path = path.partition('?')[0]
                    modified_url = '%s?%s' % (base_path, urlencode(req_data, doseq=True))
                request = Request(data=encoded_data, url=modified_url, headers=headers, method=method)
                return request

        return True