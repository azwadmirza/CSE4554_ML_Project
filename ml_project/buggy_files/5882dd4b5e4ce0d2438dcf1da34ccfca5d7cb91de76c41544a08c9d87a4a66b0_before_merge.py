    def _debug_init(self):
        # determine after which passes IR dumps should take place
        print_passes = []
        if config.DEBUG_PRINT_AFTER != "none":
            if config.DEBUG_PRINT_AFTER == "all":
                print_passes = [x.name() for (x, _) in self.passes]
            else:
                # we don't validate whether the named passes exist in this
                # pipeline the compiler may be used reentrantly and different
                # pipelines may contain different passes
                splitted = config.DEBUG_PRINT_AFTER.split(',')
                print_passes = [x.strip() for x in splitted]
        return print_passes