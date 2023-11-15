    def get_option_link_args(self, options):
        if self.gcc_type == GCC_MINGW:
            # FIXME: See GnuCCompiler.get_option_link_args
            if 'cpp_winlibs' in options:
                return options['cpp_winlibs'].value[:]
            else:
                return gnu_winlibs[:]
        return []