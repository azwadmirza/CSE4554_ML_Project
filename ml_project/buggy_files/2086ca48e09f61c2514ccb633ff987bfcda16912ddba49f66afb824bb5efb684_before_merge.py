    def find_root(self):
        """Find a function without a caller"""
        self.profdata.sort_stats("cumulative")
        for func in self.profdata.fcn_list:
            if ('~', 0) != func[0:2] and not func[2].startswith(
                    '<built-in method exec>'):
                # This skips the profiler function at the top of the list
                # it does only occur in Python 3
                return func