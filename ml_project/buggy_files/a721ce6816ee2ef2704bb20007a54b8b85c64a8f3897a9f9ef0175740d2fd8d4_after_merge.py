    def _detect_c_or_cpp_compiler(self, lang, evar, want_cross):
        popen_exceptions = {}
        compilers, ccache, is_cross, exe_wrap = self._get_compilers(lang, evar, want_cross)
        for compiler in compilers:
            if isinstance(compiler, str):
                compiler = [compiler]
            if 'cl' in compiler or 'cl.exe' in compiler:
                arg = '/?'
            else:
                arg = '--version'
            try:
                p, out, err = Popen_safe(compiler + [arg])
            except OSError as e:
                popen_exceptions[' '.join(compiler + [arg])] = e
                continue
            version = search_version(out)
            if 'Free Software Foundation' in out:
                defines = self.get_gnu_compiler_defines(compiler)
                if not defines:
                    popen_exceptions[' '.join(compiler)] = 'no pre-processor defines'
                    continue
                gtype = self.get_gnu_compiler_type(defines)
                version = self.get_gnu_version_from_defines(defines)
                cls = GnuCCompiler if lang == 'c' else GnuCPPCompiler
                return cls(ccache + compiler, version, gtype, is_cross, exe_wrap, defines)
            if 'clang' in out:
                if 'Apple' in out or for_darwin(want_cross, self):
                    cltype = CLANG_OSX
                elif 'windows' in out or for_windows(want_cross, self):
                    cltype = CLANG_WIN
                else:
                    cltype = CLANG_STANDARD
                cls = ClangCCompiler if lang == 'c' else ClangCPPCompiler
                return cls(ccache + compiler, version, cltype, is_cross, exe_wrap)
            if 'Microsoft' in out or 'Microsoft' in err:
                # Visual Studio prints version number to stderr but
                # everything else to stdout. Why? Lord only knows.
                version = search_version(err)
                cls = VisualStudioCCompiler if lang == 'c' else VisualStudioCPPCompiler
                return cls(compiler, version, is_cross, exe_wrap)
            if '(ICC)' in out:
                # TODO: add microsoft add check OSX
                inteltype = ICC_STANDARD
                cls = IntelCCompiler if lang == 'c' else IntelCPPCompiler
                return cls(ccache + compiler, version, inteltype, is_cross, exe_wrap)
        self._handle_exceptions(popen_exceptions, compilers)