    def edit_config(self, command):
        resp = list()
        responses = self.send_request(command, output='config')
        for response in to_list(responses):
            if response != '{}':
                resp.append(response)
        if not resp:
            resp = ['']

        return json.dumps(resp)