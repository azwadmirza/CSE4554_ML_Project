    def write_to_stdin(self, line):
        sw = self.get_current_shellwidget()
        if sw is not None:
            # Needed to handle an error when kernel_client is None
            # See issue 7578
            try:
                sw.write_to_stdin(line)
            except AttributeError:
                pass