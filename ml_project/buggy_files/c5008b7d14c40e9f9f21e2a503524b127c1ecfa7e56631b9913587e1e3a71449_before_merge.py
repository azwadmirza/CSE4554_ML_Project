    def run(self):

        if self.options.verbosity > 0:
            if C.CONFIG_FILE:
                display.display("Using %s as config file" % C.CONFIG_FILE)
            else:
                display.display("No config file found; using defaults")