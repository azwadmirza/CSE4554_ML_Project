    def log_to_file(self, message):
        """Write the message to the log file, if possible"""
        if self.log_file_open:
            if self.log_file_local:
                tmpstr = self.format(message, self.verbosity)
                self.logfp.write(_to_bytes(tmpstr))
                self.logfp.flush()
            else:
                self.log_file_conn.log.Log.log_to_file(message)