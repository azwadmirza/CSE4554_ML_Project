    def edit_config(self, command):
        responses = self.send_request(command, output='config')
        return json.dumps(responses)