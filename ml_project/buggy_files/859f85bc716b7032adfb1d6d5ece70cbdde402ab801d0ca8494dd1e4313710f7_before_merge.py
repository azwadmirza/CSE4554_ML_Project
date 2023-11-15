    def write(cls, error_type, rp, exc):
        """Add line to log file indicating error exc with file rp"""
        if not Globals.isbackup_writer:
            return Globals.backup_writer.log.ErrorLog.write(
                error_type, rp, exc)
        logstr = cls.get_log_string(error_type, rp, exc)
        Log(logstr, 2)
        if isinstance(logstr, bytes):
            logstr = logstr.decode('utf-8')
        if Globals.null_separator:
            logstr += "\0"
        else:
            logstr = re.sub("\n", " ", logstr)
            logstr += "\n"
        cls._log_fileobj.write(logstr)