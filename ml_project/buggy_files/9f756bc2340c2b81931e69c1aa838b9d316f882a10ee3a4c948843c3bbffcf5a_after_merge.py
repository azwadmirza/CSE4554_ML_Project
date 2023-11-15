    def start_process(self, index, diff_rorp):
        """Start processing directory"""
        self.base_rp, inc_prefix = longname.get_mirror_inc_rps(
            self.CCPP.get_rorps(index), self.basis_root_rp, self.inc_root_rp)
        self.base_rp.setdata()
        assert diff_rorp.isdir() or self.base_rp.isdir(), \
            ("Either %s or %s must be a directory" % (repr(diff_rorp.get_safeindexpath()),
             repr(self.base_rp.get_safepath())))
        if diff_rorp.isdir():
            inc = increment.Increment(diff_rorp, self.base_rp, inc_prefix)
            if inc and inc.isreg():
                inc.fsync_with_dir()  # must write inc before rp changed
            self.base_rp.setdata()  # in case written by increment above
            self.prepare_dir(diff_rorp, self.base_rp)
        elif self.set_dir_replacement(diff_rorp, self.base_rp):
            inc = increment.Increment(self.dir_replacement, self.base_rp,
                                      inc_prefix)
            if inc:
                self.CCPP.set_inc(index, inc)
                self.CCPP.flag_success(index)