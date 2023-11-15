    def write_to_stdin(self, line):
        sw = self.get_current_shellwidget()
        if sw is not None:
            sw.write_to_stdin(line)