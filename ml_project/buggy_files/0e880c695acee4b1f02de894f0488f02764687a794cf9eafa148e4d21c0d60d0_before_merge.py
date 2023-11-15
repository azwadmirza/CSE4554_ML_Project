    def UpdateDownloadFilters(self):
        proccessedfilters = []
        outfilter = "(\\\\("
        failed = {}
        df = self.np.config.sections["transfers"]["downloadfilters"]
        df.sort()
        # Get Filters from config file and check their escaped status
        # Test if they are valid regular expressions and save error messages

        for item in df:
            filter, escaped = item
            if escaped:
                dfilter = re.escape(filter)
                dfilter = dfilter.replace("\\*", ".*")
            else:
                dfilter = filter
            try:
                re.compile("(" + dfilter + ")")
                outfilter += dfilter
                proccessedfilters.append(dfilter)
            except Exception as e:
                failed[dfilter] = e

            proccessedfilters.append(dfilter)

            if item is not df[-1]:
                outfilter += "|"

        # Crop trailing pipes
        while outfilter[-1] == "|":
            outfilter = outfilter[:-1]

        outfilter += ")$)"
        try:
            re.compile(outfilter)
            self.np.config.sections["transfers"]["downloadregexp"] = outfilter
            # Send error messages for each failed filter to log window
            if len(list(failed.keys())) >= 1:
                errors = ""
                for filter, error in list(failed.items()):
                    errors += "Filter: %s Error: %s " % (filter, error)
                error = _("Error: %(num)d Download filters failed! %(error)s " % {'num': len(list(failed.keys())), 'error': errors})
                self.logMessage(error)
        except Exception as e:
            # Strange that individual filters _and_ the composite filter both fail
            self.logMessage(_("Error: Download Filter failed! Verify your filters. Reason: %s" % e))
            self.np.config.sections["transfers"]["downloadregexp"] = ""