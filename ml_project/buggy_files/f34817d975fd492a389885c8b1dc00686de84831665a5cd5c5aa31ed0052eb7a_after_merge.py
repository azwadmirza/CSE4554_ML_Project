    def execute(self, code, timeout=DEFAULT_TIMEOUT):
        """
        Executes the code provided and returns the result of that execution.
        """
        response = []
        try:
            msg_id = self._send_request(code)

            post_idle = False
            while True:
                response_message = self._get_response(msg_id, timeout, post_idle)
                if response_message:
                    response_message_type = response_message['msg_type']

                    if response_message_type == 'error':
                        response.append('{}:{}:{}'.format(response_message['content']['ename'],
                                                          response_message['content']['evalue'],
                                                          response_message['content']['traceback']))
                    elif response_message_type == 'stream':
                        response.append(Kernel._convert_raw_response(response_message['content']['text']))

                    elif response_message_type == 'execute_result' or response_message_type == 'display_data':
                        if 'text/plain' in response_message['content']['data']:
                            response.append(
                                Kernel._convert_raw_response(response_message['content']['data']['text/plain']))
                        elif 'text/html' in response_message['content']['data']:
                            response.append(
                                Kernel._convert_raw_response(response_message['content']['data']['text/html']))

                    elif response_message_type == 'status':
                        if response_message['content']['execution_state'] == 'idle':
                            post_idle = True  # indicate we're at the logical end and timeout poll for next message
                            continue

                if post_idle and response_message is None:
                    break

        except BaseException as b:
            print(b)

        return ''.join(response)