    def log_to_file(self, message):
        """Write the message to the log file, if possible"""
        if self.log_file_open:
            if self.log_file_local:
                tmpstr = self.format(message, self.verbosity)
                if type(tmpstr) == str:  # transform string in bytes
                    tmpstr = tmpstr.encode('utf-8', 'backslashreplace')
                self.logfp.write(tmpstr)
                self.logfp.flush()
            else:
                self.log_file_conn.log.Log.log_to_file(message)