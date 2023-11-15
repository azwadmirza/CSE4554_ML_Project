    def __str__(self):
        try:
            return text_type(self.message % self._kwargs)
        except:
            debug_message = "\n".join((
                "class: " + self.__class__.__name__,
                "message:",
                self.message,
                "kwargs:",
                text_type(self._kwargs),
                "",
            ))
            sys.stderr.write(debug_message)
            raise