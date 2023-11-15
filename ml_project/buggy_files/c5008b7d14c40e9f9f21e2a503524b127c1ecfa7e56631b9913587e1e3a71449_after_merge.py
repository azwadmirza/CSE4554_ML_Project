    def run(self):

        if self.options.verbosity > 0:
            if C.CONFIG_FILE:
                display.display(u"Using %s as config file" % to_unicode(C.CONFIG_FILE))
            else:
                display.display(u"No config file found; using defaults")