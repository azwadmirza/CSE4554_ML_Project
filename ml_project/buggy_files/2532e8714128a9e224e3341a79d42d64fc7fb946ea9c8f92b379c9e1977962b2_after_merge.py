    def OnVerifyFilter(self, widget):

        outfilter = "(\\\\("

        df = list(self.filtersiters.keys())
        df.sort()

        proccessedfilters = []
        failed = {}

        for filter in df:

            iter = self.filtersiters[filter]
            dfilter = self.filterlist.get_value(iter, 0)
            escaped = self.filterlist.get_value(iter, 1)

            if escaped:
                dfilter = re.escape(dfilter)
                dfilter = dfilter.replace("\\*", ".*")

            try:
                re.compile("(" + dfilter + ")")
                outfilter += dfilter
                proccessedfilters.append(dfilter)
            except Exception as e:
                failed[dfilter] = e

            if filter is not df[-1]:
                outfilter += "|"

        outfilter += ")$)"

        try:
            re.compile(outfilter)

        except Exception as e:
            failed[outfilter] = e

        if len(failed) >= 1:
            errors = ""

            for filter, error in list(failed.items()):
                errors += "Filter: %(filter)s Error: %(error)s " % {
                    'filter': filter,
                    'error': error
                }

            error = _("%(num)d Failed! %(error)s " % {
                'num': len(failed),
                'error': errors}
            )

            self.VerifiedLabel.set_markup("<span color=\"red\" weight=\"bold\">%s</span>" % error)
        else:
            self.VerifiedLabel.set_markup("<b>Filters Successful</b>")