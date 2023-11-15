    def edit_config(self, commands=None):
        for cmd in chain(to_list(commands)):
            try:
                if isinstance(cmd, str):
                    cmd = json.loads(cmd)
                command = cmd.get('command', None)
                prompt = cmd.get('prompt', None)
                answer = cmd.get('answer', None)
                sendonly = cmd.get('sendonly', False)
                newline = cmd.get('newline', True)
            except:
                command = cmd
                prompt = None
                answer = None
                sendonly = None
                newline = None

            self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline)