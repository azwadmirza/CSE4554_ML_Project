    def detect_objcpp_compiler(self, want_cross):
        popen_exceptions = {}
        compilers, ccache, is_cross, exe_wrap = self._get_compilers('objcpp', 'OBJCXX', want_cross)
        for compiler in compilers:
            if isinstance(compiler, str):
                compiler = [compiler]
            arg = ['--version']
            try:
                p, out, err = Popen_safe(compiler + arg)
            except OSError as e:
                popen_exceptions[' '.join(compiler + arg)] = e
            version = search_version(out)
            if 'Free Software Foundation' in out:
                defines = self.get_gnu_compiler_defines(compiler)
                if not defines:
                    popen_exceptions[compiler] = 'no pre-processor defines'
                    continue
                gtype = self.get_gnu_compiler_type(defines)
                version = self.get_gnu_version_from_defines(defines)
                return GnuObjCPPCompiler(ccache + compiler, version, gtype, is_cross, exe_wrap, defines)
            if out.startswith('Apple LLVM'):
                return ClangObjCPPCompiler(ccache + compiler, version, CLANG_OSX, is_cross, exe_wrap)
            if out.startswith('clang'):
                return ClangObjCPPCompiler(ccache + compiler, version, CLANG_STANDARD, is_cross, exe_wrap)
        self._handle_exceptions(popen_exceptions, compilers)