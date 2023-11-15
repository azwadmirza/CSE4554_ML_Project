    def get_option_link_args(self, options):
        # FIXME: See GnuCCompiler.get_option_link_args
        if 'c_winlibs' in options:
            return options['c_winlibs'].value[:]
        else:
            return msvc_winlibs[:]