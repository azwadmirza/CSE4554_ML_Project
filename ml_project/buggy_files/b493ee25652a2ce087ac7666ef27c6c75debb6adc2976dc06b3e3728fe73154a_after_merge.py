    def get_option_link_args(self, options):
        if self.gcc_type == GCC_MINGW:
            # FIXME: This check is needed because we currently pass
            # cross-compiler options to the native compiler too and when
            # cross-compiling from Windows to Linux, `options` will contain
            # Linux-specific options which doesn't include `c_winlibs`. The
            # proper fix is to allow cross-info files to specify compiler
            # options and to maintain both cross and native compiler options in
            # coredata: https://github.com/mesonbuild/meson/issues/1029
            if 'c_winlibs' in options:
                return options['c_winlibs'].value[:]
            else:
                return gnu_winlibs[:]
        return []