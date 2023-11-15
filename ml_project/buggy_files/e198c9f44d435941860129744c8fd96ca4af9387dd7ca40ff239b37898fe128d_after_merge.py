    def _finalize(self, commands, ext):
        commands = concatv(commands, ('',))  # add terminating newline
        if ext is None:
            output = self.command_join.join(commands)
            if PY2:
                return ensure_binary(output)
            return output
        elif ext:
            with NamedTemporaryFile('w+b', suffix=ext, delete=False) as tf:
                # the default mode is 'w+b', and universal new lines don't work in that mode
                # command_join should account for that
                tf.write(ensure_binary(self.command_join.join(commands)))
            return tf.name
        else:
            raise NotImplementedError()