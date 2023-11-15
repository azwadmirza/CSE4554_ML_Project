    def param_parse(v, pimode=False):
        for i, e in enumerate(v):
            if pimode:
                v[i] = MatplotlibDrawer.format_pi(e)
            else:
                v[i] = MatplotlibDrawer.format_numeric(e)
            if v[i].startswith('-'):
                v[i] = '$-$' + v[i][1:]
        param = ', '.join(v)
        return param