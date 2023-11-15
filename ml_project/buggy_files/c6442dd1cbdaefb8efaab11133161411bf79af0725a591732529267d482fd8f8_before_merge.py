    def single_string(self):
        """Creates a long string with the ascii art.

        Returns:
            str: The lines joined by a newline (``\\n``)
        """
        return "\n".join(self.lines())