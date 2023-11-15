    def find_root(self):
        """Find a function without a caller"""
        # Fixes spyder-ide/spyder#8336
        if self.profdata is not None:
            self.profdata.sort_stats("cumulative")
        else:
            return
        for func in self.profdata.fcn_list:
            if ('~', 0) != func[0:2] and not func[2].startswith(
                    '<built-in method exec>'):
                # This skips the profiler function at the top of the list
                # it does only occur in Python 3
                return func