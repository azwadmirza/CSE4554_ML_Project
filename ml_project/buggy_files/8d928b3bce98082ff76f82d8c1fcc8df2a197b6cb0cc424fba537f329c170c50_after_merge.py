    def __arg_comps(self):
        '''
        Return the function name and the arg list
        '''
        fun = self.argv[0] if self.argv else ''
        parsed = salt.utils.args.parse_input(
            self.argv[1:],
            condition=False,
            no_parse=self.opts.get('no_parse', []))
        args = parsed[0]
        kws = parsed[1]
        return fun, args, kws