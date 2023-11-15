    def set_case_sensitive_readwrite(self, subdir):
        """Determine if directory at rp is case sensitive by writing"""
        assert not self.read_only
        upper_a = subdir.append("A")
        upper_a.touch()
        lower_a = subdir.append("a")
        if lower_a.lstat():
            lower_a.delete()
            upper_a.setdata()
            assert not upper_a.lstat()
            self.case_sensitive = 0
        else:
            upper_a.delete()
            self.case_sensitive = 1