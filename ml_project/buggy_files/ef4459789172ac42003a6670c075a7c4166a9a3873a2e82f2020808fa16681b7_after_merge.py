    def flush(self, error=False, prompt=False):
        """Flush buffer, write text to console"""
        # Fix for Issue 2452 
        if PY3:
            try:
                text = "".join(self.__buffer)
            except TypeError:
                text = b"".join(self.__buffer)
                text = text.decode( locale.getdefaultlocale()[1] )
        else:
            text = "".join(self.__buffer)

        self.__buffer = []
        self.insert_text(text, at_end=True, error=error, prompt=prompt)
        QCoreApplication.processEvents()
        self.repaint()
        # Clear input buffer:
        self.new_input_line = True