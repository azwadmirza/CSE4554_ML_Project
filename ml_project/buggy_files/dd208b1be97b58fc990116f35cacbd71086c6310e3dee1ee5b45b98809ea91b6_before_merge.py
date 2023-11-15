    def open(cls, time_string, compress=1):
        """Open the error log, prepare for writing"""
        if not Globals.isbackup_writer:
            return Globals.backup_writer.log.ErrorLog.open(
                time_string, compress)
        assert not cls._log_fileobj, "log already open"
        assert Globals.isbackup_writer

        base_rp = Globals.rbdir.append("error_log.%s.data" % (time_string, ))
        if compress:
            cls._log_fileobj = rpath.MaybeGzip(base_rp)
        else:
            cls._log_fileobj = base_rp.open("wb", compress=0)