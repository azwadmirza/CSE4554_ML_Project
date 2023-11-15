        def callback(text):
            if not text or text[0] not in modeparsers.STARTCHARS:
                message.error('command must start with one of {}'
                              .format(modeparsers.STARTCHARS))
                return
            self.set_cmd_text(text)
            if run:
                self.command_accept()