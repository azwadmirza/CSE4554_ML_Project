    def _send_message(self, path, data, req_data, headers):
        queue_url = self._queue_url(path, req_data, headers)
        queue_name = queue_url[queue_url.rindex('/') + 1:]
        message_body = req_data.get('MessageBody', [None])[0]
        message_attributes = self.format_message_attributes(req_data)
        region_name = extract_region_from_auth_header(headers)

        process_result = lambda_api.process_sqs_message(message_body,
            message_attributes, queue_name, region_name=region_name)
        if process_result:
            # If a Lambda was listening, do not add the message to the queue
            new_response = Response()
            new_response._content = SUCCESSFUL_SEND_MESSAGE_XML_TEMPLATE.format(
                message_attr_hash=md5(data),
                message_body_hash=md5(message_body),
                message_id=str(uuid.uuid4())
            )
            new_response.status_code = 200
            return new_response