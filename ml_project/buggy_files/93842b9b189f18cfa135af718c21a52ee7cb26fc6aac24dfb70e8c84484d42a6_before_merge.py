    def run_commands(self, commands):
        """Runs list of commands on remote device and returns results
        """
        output = None
        queue = list()
        responses = list()

        def _send(commands, output):
            response = self.send_request(commands, output=output)
            if 'error' in response:
                err = response['error']
                self._module.fail_json(msg=err['message'], code=err['code'])
            return response['result']

        for item in to_list(commands):
            if is_json(item['command']):
                item['command'] = str(item['command']).replace('| json', '')
                item['output'] = 'json'

            if output and output != item['output']:
                responses.extend(_send(queue, output))
                queue = list()

            output = item['output'] or 'json'
            queue.append(item['command'])

        if queue:
            responses.extend(_send(queue, output))

        for index, item in enumerate(commands):
            try:
                responses[index] = responses[index]['output'].strip()
            except KeyError:
                pass

        return responses