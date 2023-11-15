    def _maybe_convert_ynames_int(self, ynames):
        # see if they're integers
        try:
            for i in ynames:
                if ynames[i] % 1 == 0:
                    ynames[i] = str(int(ynames[i]))
        except TypeError:
            pass
        return ynames