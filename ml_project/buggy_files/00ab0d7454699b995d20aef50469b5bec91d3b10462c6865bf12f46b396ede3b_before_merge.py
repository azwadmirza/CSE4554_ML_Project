    def edit_config(self, command):
        responses = []
        for cmd in chain(['configure'], to_list(command), ['end']):
            responses.append(self.send_command(cmd))

        return json.dumps(responses)