    def run_commands(self, commands, check_rc=True):
        """Run list of commands on remote device and return results
        """
        responses = list()
        connection = self._get_connection()

        for cmd in to_list(commands):
            if isinstance(cmd, dict):
                command = cmd['command']
                prompt = cmd['prompt']
                answer = cmd['answer']
            else:
                command = cmd
                prompt = None
                answer = None

            try:
                out = connection.get(command, prompt, answer)
            except ConnectionError as exc:
                if check_rc:
                    raise
                out = getattr(exc, 'err', exc)
            out = to_text(out, errors='surrogate_or_strict')

            try:
                out = self._module.from_json(out)
            except ValueError:
                out = str(out).strip()

            responses.append(out)

        return responses