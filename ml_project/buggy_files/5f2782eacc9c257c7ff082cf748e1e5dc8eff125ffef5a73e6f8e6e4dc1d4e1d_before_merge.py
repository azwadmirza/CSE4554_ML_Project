    def get_measurement(self):
        """ Determine if the return value of the command is a number """
        out, err, status = cmd_output(self.command)
        if str_is_float(out):
            return float(out)
        else:
            return None