    def get_option_link_args(self, options):
        if self.gcc_type == GCC_MINGW:
            return options['c_winlibs'].value
        return []