    def param_parse(v, pimode=False):
        for i, e in enumerate(v):
            if pimode:
                try:
                    v[i] = MatplotlibDrawer.format_pi(e)
                except TypeError:
                    v[i] = str(e)
            else:
                try:
                    v[i] = MatplotlibDrawer.format_numeric(e)
                except TypeError:
                    v[i] = str(e)
            if v[i].startswith('-'):
                v[i] = '$-$' + v[i][1:]
        param = ', '.join(v)
        return param