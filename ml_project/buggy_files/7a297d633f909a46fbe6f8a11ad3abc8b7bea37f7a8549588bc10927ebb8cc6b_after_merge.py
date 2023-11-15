    def get(self, command=None, prompt=None, answer=None, sendonly=False, newline=True, output=None):
        if output:
            raise ValueError("'output' value %s is not supported for get" % output)
        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline)