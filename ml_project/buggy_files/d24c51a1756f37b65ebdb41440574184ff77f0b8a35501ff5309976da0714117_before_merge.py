    def detect_fortran_compiler(self, want_cross):
        popen_exceptions = {}
        compilers, ccache, is_cross, exe_wrap = self._get_compilers('fortran', 'FC', want_cross)
        for compiler in compilers:
            if isinstance(compiler, str):
                compiler = [compiler]
            for arg in ['--version', '-V']:
                try:
                    p, out, err = Popen_safe(compiler + [arg])
                except OSError as e:
                    popen_exceptions[' '.join(compiler + [arg])] = e
                    continue

                version = search_version(out)

                if 'GNU Fortran' in out:
                    defines = self.get_gnu_compiler_defines(compiler)
                    if not defines:
                        popen_exceptions[compiler] = 'no pre-processor defines'
                        continue
                    gtype = self.get_gnu_compiler_type(defines)
                    version = self.get_gnu_version_from_defines(defines)
                    return GnuFortranCompiler(compiler, version, gtype, is_cross, exe_wrap, defines)

                if 'G95' in out:
                    return G95FortranCompiler(compiler, version, is_cross, exe_wrap)

                if 'Sun Fortran' in err:
                    version = search_version(err)
                    return SunFortranCompiler(compiler, version, is_cross, exe_wrap)

                if 'ifort (IFORT)' in out:
                    return IntelFortranCompiler(compiler, version, is_cross, exe_wrap)

                if 'PathScale EKOPath(tm)' in err:
                    return PathScaleFortranCompiler(compiler, version, is_cross, exe_wrap)

                if 'PGI Compilers' in out:
                    return PGIFortranCompiler(compiler, version, is_cross, exe_wrap)

                if 'Open64 Compiler Suite' in err:
                    return Open64FortranCompiler(compiler, version, is_cross, exe_wrap)

                if 'NAG Fortran' in err:
                    return NAGFortranCompiler(compiler, version, is_cross, exe_wrap)
        self._handle_exceptions(popen_exceptions, compilers)