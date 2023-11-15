    def _debug_init(self):
        # determine after which passes IR dumps should take place
        def parse(conf_item):
            print_passes = []
            if conf_item != "none":
                if conf_item == "all":
                    print_passes = [x.name() for (x, _) in self.passes]
                else:
                    # we don't validate whether the named passes exist in this
                    # pipeline the compiler may be used reentrantly and
                    # different pipelines may contain different passes
                    splitted = conf_item.split(',')
                    print_passes = [x.strip() for x in splitted]
            return print_passes
        ret = (parse(config.DEBUG_PRINT_AFTER),
               parse(config.DEBUG_PRINT_BEFORE),
               parse(config.DEBUG_PRINT_WRAP),)
        return ret