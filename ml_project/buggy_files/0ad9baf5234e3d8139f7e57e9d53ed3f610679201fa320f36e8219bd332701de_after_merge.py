    def set_case_sensitive_readwrite(self, subdir):
        """Determine if directory at rp is case sensitive by writing"""
        assert not self.read_only
        upper_a = subdir.append("A")
        upper_a.touch()
        lower_a = subdir.append("a")
        if lower_a.lstat():
            lower_a.delete()
            upper_a.setdata()
            if upper_a.lstat():
                # we know that (fuse-)exFAT 1.3.0 takes 1sec to register the
                # deletion (July 2020)
                log.Log.FatalError(
                    "We're sorry but the target file system at '%s' isn't "
                    "deemed reliable enough for a backup. It takes too long "
                    "or doesn't register case insensitive deletion of files."
                    % subdir.get_safepath())
            self.case_sensitive = 0
        else:
            upper_a.delete()
            self.case_sensitive = 1