    def configure(self, extra_cmake_options: T.List[str]) -> None:
        for_machine = MachineChoice.HOST # TODO make parameter
        # Find CMake
        cmake_exe = CMakeExecutor(self.env, '>=3.7', for_machine)
        if not cmake_exe.found():
            raise CMakeException('Unable to find CMake')
        self.trace = CMakeTraceParser(cmake_exe.version(), self.build_dir, permissive=True)

        preload_file = Path(__file__).resolve().parent / 'data' / 'preload.cmake'

        # Prefere CMAKE_PROJECT_INCLUDE over CMAKE_TOOLCHAIN_FILE if possible,
        # since CMAKE_PROJECT_INCLUDE was actually designed for code injection.
        preload_var = 'CMAKE_PROJECT_INCLUDE'
        if version_compare(cmake_exe.version(), '<3.15'):
            preload_var = 'CMAKE_TOOLCHAIN_FILE'

        generator = backend_generator_map[self.backend_name]
        cmake_args = []
        trace_args = self.trace.trace_args()
        cmcmp_args = ['-DCMAKE_POLICY_WARNING_{}=OFF'.format(x) for x in disable_policy_warnings]
        pload_args = ['-D{}={}'.format(preload_var, str(preload_file))]

        if version_compare(cmake_exe.version(), '>=3.14'):
            self.cmake_api = CMakeAPI.FILE
            self.fileapi.setup_request()

        # Map meson compiler to CMake variables
        for lang, comp in self.env.coredata.compilers[for_machine].items():
            if lang not in language_map:
                continue
            self.linkers.add(comp.get_linker_id())
            cmake_lang = language_map[lang]
            exelist = comp.get_exelist()
            if len(exelist) == 1:
                cmake_args += ['-DCMAKE_{}_COMPILER={}'.format(cmake_lang, exelist[0])]
            elif len(exelist) == 2:
                cmake_args += ['-DCMAKE_{}_COMPILER_LAUNCHER={}'.format(cmake_lang, exelist[0]),
                               '-DCMAKE_{}_COMPILER={}'.format(cmake_lang, exelist[1])]
            if hasattr(comp, 'get_linker_exelist') and comp.get_id() == 'clang-cl':
                cmake_args += ['-DCMAKE_LINKER={}'.format(comp.get_linker_exelist()[0])]
        cmake_args += ['-G', generator]
        cmake_args += ['-DCMAKE_INSTALL_PREFIX={}'.format(self.install_prefix)]
        cmake_args += extra_cmake_options

        # Run CMake
        mlog.log()
        with mlog.nested():
            mlog.log('Configuring the build directory with', mlog.bold('CMake'), 'version', mlog.cyan(cmake_exe.version()))
            mlog.log(mlog.bold('Running:'), ' '.join(cmake_args))
            mlog.log(mlog.bold('  - build directory:         '), self.build_dir)
            mlog.log(mlog.bold('  - source directory:        '), self.src_dir)
            mlog.log(mlog.bold('  - trace args:              '), ' '.join(trace_args))
            mlog.log(mlog.bold('  - preload file:            '), str(preload_file))
            mlog.log(mlog.bold('  - disabled policy warnings:'), '[{}]'.format(', '.join(disable_policy_warnings)))
            mlog.log()
            os.makedirs(self.build_dir, exist_ok=True)
            os_env = os.environ.copy()
            os_env['LC_ALL'] = 'C'
            final_args = cmake_args + trace_args + cmcmp_args + pload_args + [self.src_dir]

            cmake_exe.set_exec_mode(print_cmout=True, always_capture_stderr=self.trace.requires_stderr())
            rc, _, self.raw_trace = cmake_exe.call(final_args, self.build_dir, env=os_env, disable_cache=True)

        mlog.log()
        h = mlog.green('SUCCEEDED') if rc == 0 else mlog.red('FAILED')
        mlog.log('CMake configuration:', h)
        if rc != 0:
            raise CMakeException('Failed to configure the CMake subproject')