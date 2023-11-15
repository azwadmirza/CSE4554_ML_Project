    def get_option_link_args(self, options):
        # FIXME: See GnuCCompiler.get_option_link_args
        if 'cpp_winlibs' in options:
            return options['cpp_winlibs'].value[:]
        else:
            return msvc_winlibs[:]