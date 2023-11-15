        def callback(text):
            self.set_cmd_text(text)
            if run:
                self.command_accept()