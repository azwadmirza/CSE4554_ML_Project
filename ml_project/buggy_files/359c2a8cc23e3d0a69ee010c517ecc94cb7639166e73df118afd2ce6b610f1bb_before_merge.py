    def get_option_link_args(self, options):
        if self.gcc_type == GCC_MINGW:
            return options['cpp_winlibs'].value
        return []