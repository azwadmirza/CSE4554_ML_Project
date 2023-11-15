    def open_logfile_local(self, rpath):
        """Open logfile locally - should only be run on one connection"""
        assert rpath.conn is Globals.local_connection
        try:
            self.logfp = rpath.open("a")
        except (OSError, IOError) as e:
            raise LoggerError(
                "Unable to open logfile %s: %s" % (rpath.path, e))
        self.log_file_local = 1
        self.logrp = rpath