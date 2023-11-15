    def build(self, directory='output',
              compile=True, run=True, debug=False, clean=False,
              with_output=True, additional_source_files=None,
              run_args=None, direct_call=True, **kwds):
        '''
        Build the project

        TODO: more details

        Parameters
        ----------
        directory : str, optional
            The output directory to write the project to, any existing files
            will be overwritten. If the given directory name is ``None``, then
            a temporary directory will be used (used in the test suite to avoid
            problems when running several tests in parallel). Defaults to
            ``'output'``.
        compile : bool, optional
            Whether or not to attempt to compile the project. Defaults to
            ``True``.
        run : bool, optional
            Whether or not to attempt to run the built project if it
            successfully builds. Defaults to ``True``.
        debug : bool, optional
            Whether to compile in debug mode. Defaults to ``False``.
        with_output : bool, optional
            Whether or not to show the ``stdout`` of the built program when run.
            Output will be shown in case of compilation or runtime error.
            Defaults to ``True``.
        clean : bool, optional
            Whether or not to clean the project before building. Defaults to
            ``False``.
        additional_source_files : list of str, optional
            A list of additional ``.cpp`` files to include in the build.
        direct_call : bool, optional
            Whether this function was called directly. Is used internally to
            distinguish an automatic build due to the ``build_on_run`` option
            from a manual ``device.build`` call.
        '''
        if self.build_on_run and direct_call:
            raise RuntimeError('You used set_device with build_on_run=True '
                               '(the default option), which will automatically '
                               'build the simulation at the first encountered '
                               'run call - do not call device.build manually '
                               'in this case. If you want to call it manually, '
                               'e.g. because you have multiple run calls, use '
                               'set_device with build_on_run=False.')
        if self.has_been_run:
            raise RuntimeError('The network has already been built and run '
                               'before. To build several simulations in '
                               'the same script, call "device.reinit()" '
                               'and "device.activate()". Note that you '
                               'will have to set build options (e.g. the '
                               'directory) and defaultclock.dt again.')
        renames = {'project_dir': 'directory',
                   'compile_project': 'compile',
                   'run_project': 'run'}
        if len(kwds):
            msg = ''
            for kwd in kwds:
                if kwd in renames:
                    msg += ("Keyword argument '%s' has been renamed to "
                            "'%s'. ") % (kwd, renames[kwd])
                else:
                    msg += "Unknown keyword argument '%s'. " % kwd
            raise TypeError(msg)

        if additional_source_files is None:
            additional_source_files = []
        if run_args is None:
            run_args = []
        if directory is None:
            directory = tempfile.mkdtemp(prefix='brian_standalone_')
        self.project_dir = directory
        ensure_directory(directory)

        # Determine compiler flags and directories
        compiler, default_extra_compile_args = get_compiler_and_args()
        extra_compile_args = self.extra_compile_args + default_extra_compile_args
        extra_link_args = self.extra_link_args + prefs['codegen.cpp.extra_link_args']

        codeobj_define_macros = [macro for codeobj in
                                 self.code_objects.values()
                                 for macro in
                                 codeobj.compiler_kwds.get('define_macros', [])]
        define_macros = (self.define_macros +
                         prefs['codegen.cpp.define_macros'] +
                         codeobj_define_macros)

        codeobj_include_dirs = [include_dir for codeobj in
                                self.code_objects.values()
                                for include_dir in
                                codeobj.compiler_kwds.get('include_dirs', [])]
        include_dirs = (self.include_dirs +
                        prefs['codegen.cpp.include_dirs'] +
                        codeobj_include_dirs)

        codeobj_library_dirs = [library_dir for codeobj in
                                self.code_objects.values()
                                for library_dir in
                                codeobj.compiler_kwds.get('library_dirs', [])]
        library_dirs = (self.library_dirs +
                        prefs['codegen.cpp.library_dirs'] +
                        codeobj_library_dirs)

        codeobj_runtime_dirs = [runtime_dir for codeobj in
                                self.code_objects.values()
                                for runtime_dir in
                                codeobj.compiler_kwds.get('runtime_library_dirs', [])]
        runtime_library_dirs = (self.runtime_library_dirs +
                                prefs['codegen.cpp.runtime_library_dirs'] +
                                codeobj_runtime_dirs)

        codeobj_libraries = [library for codeobj in
                             self.code_objects.values()
                             for library in
                             codeobj.compiler_kwds.get('libraries', [])]
        libraries = (self.libraries +
                     prefs['codegen.cpp.libraries'] +
                     codeobj_libraries)

        compiler_obj = ccompiler.new_compiler(compiler=compiler)
        compiler_flags = (ccompiler.gen_preprocess_options(define_macros,
                                                           include_dirs) +
                          extra_compile_args)
        linker_flags = (ccompiler.gen_lib_options(compiler_obj,
                                                  library_dirs=library_dirs,
                                                  runtime_library_dirs=runtime_library_dirs,
                                                  libraries=libraries) +
                        extra_link_args)

        codeobj_source_files = [source_file for codeobj in
                                self.code_objects.values()
                                for source_file in
                                codeobj.compiler_kwds.get('sources', [])]
        additional_source_files += (codeobj_source_files +
                                    ['brianlib/randomkit/randomkit.c'])

        for d in ['code_objects', 'results', 'static_arrays']:
            ensure_directory(os.path.join(directory, d))

        self.writer = CPPWriter(directory)

        # Get the number of threads if specified in an openmp context
        nb_threads = prefs.devices.cpp_standalone.openmp_threads
        # If the number is negative, we need to throw an error
        if (nb_threads < 0):
            raise ValueError('The number of OpenMP threads can not be negative !')

        logger.diagnostic("Writing C++ standalone project to directory "+os.path.normpath(directory))

        self.check_openmp_compatible(nb_threads)

        self.write_static_arrays(directory)
        self.find_synapses()

        # Not sure what the best place is to call Network.after_run -- at the
        # moment the only important thing it does is to clear the objects stored
        # in magic_network. If this is not done, this might lead to problems
        # for repeated runs of standalone (e.g. in the test suite).
        for net in self.networks:
            net.after_run()

        # Check that all names are globally unique
        names = [obj.name for net in self.networks for obj in net.objects]
        non_unique_names = [name for name, count in Counter(names).items()
                            if count > 1]
        if len(non_unique_names):
            formatted_names = ', '.join("'%s'" % name
                                        for name in non_unique_names)
            raise ValueError('All objects need to have unique names in '
                             'standalone mode, the following name(s) were used '
                             'more than once: %s' % formatted_names)

        self.generate_objects_source(self.writer, self.arange_arrays,
                                     self.net_synapses, self.static_array_specs,
                                     self.networks)
        self.generate_main_source(self.writer)
        self.generate_codeobj_source(self.writer)
        self.generate_network_source(self.writer, compiler)
        self.generate_synapses_classes_source(self.writer)
        self.generate_run_source(self.writer)
        self.copy_source_files(self.writer, directory)

        self.writer.source_files.extend(additional_source_files)

        self.generate_makefile(self.writer, compiler,
                               compiler_flags=' '.join(compiler_flags),
                               linker_flags=' '.join(linker_flags),
                               nb_threads=nb_threads,
                               debug=debug)

        if compile:
            self.compile_source(directory, compiler, debug, clean)
            if run:
                self.run(directory, with_output, run_args)