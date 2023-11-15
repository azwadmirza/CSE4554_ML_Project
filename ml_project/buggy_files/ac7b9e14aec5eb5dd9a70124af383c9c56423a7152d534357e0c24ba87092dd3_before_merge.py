    def get(self, command, prompt=None, answer=None, sendonly=False):
        return self.send_command(to_bytes(command), prompt=to_bytes(prompt), answer=to_bytes(answer), sendonly=sendonly)