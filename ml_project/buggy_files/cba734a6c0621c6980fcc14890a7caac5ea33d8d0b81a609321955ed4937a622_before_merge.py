    def pretend_to_be_meson(self) -> CodeBlockNode:
        if not self.project_name:
            raise CMakeException('CMakeInterpreter was not analysed')

        def token(tid: str = 'string', val='') -> Token:
            return Token(tid, self.subdir, 0, 0, 0, None, val)

        def string(value: str) -> StringNode:
            return StringNode(token(val=value))

        def id_node(value: str) -> IdNode:
            return IdNode(token(val=value))

        def number(value: int) -> NumberNode:
            return NumberNode(token(val=value))

        def nodeify(value):
            if isinstance(value, str):
                return string(value)
            elif isinstance(value, bool):
                return BooleanNode(token(val=value))
            elif isinstance(value, int):
                return number(value)
            elif isinstance(value, list):
                return array(value)
            return value

        def indexed(node: BaseNode, index: int) -> IndexNode:
            return IndexNode(node, nodeify(index))

        def array(elements) -> ArrayNode:
            args = ArgumentNode(token())
            if not isinstance(elements, list):
                elements = [args]
            args.arguments += [nodeify(x) for x in elements if x is not None]
            return ArrayNode(args, 0, 0, 0, 0)

        def function(name: str, args=None, kwargs=None) -> FunctionNode:
            args = [] if args is None else args
            kwargs = {} if kwargs is None else kwargs
            args_n = ArgumentNode(token())
            if not isinstance(args, list):
                args = [args]
            args_n.arguments = [nodeify(x) for x in args if x is not None]
            args_n.kwargs = {id_node(k): nodeify(v) for k, v in kwargs.items() if v is not None}
            func_n = FunctionNode(self.subdir, 0, 0, 0, 0, name, args_n)
            return func_n

        def method(obj: BaseNode, name: str, args=None, kwargs=None) -> MethodNode:
            args = [] if args is None else args
            kwargs = {} if kwargs is None else kwargs
            args_n = ArgumentNode(token())
            if not isinstance(args, list):
                args = [args]
            args_n.arguments = [nodeify(x) for x in args if x is not None]
            args_n.kwargs = {id_node(k): nodeify(v) for k, v in kwargs.items() if v is not None}
            return MethodNode(self.subdir, 0, 0, obj, name, args_n)

        def assign(var_name: str, value: BaseNode) -> AssignmentNode:
            return AssignmentNode(self.subdir, 0, 0, var_name, value)

        # Generate the root code block and the project function call
        root_cb = CodeBlockNode(token())
        root_cb.lines += [function('project', [self.project_name] + self.languages)]

        # Add the run script for custom commands
        run_script = '{}/data/run_ctgt.py'.format(os.path.dirname(os.path.realpath(__file__)))
        run_script_var = 'ctgt_run_script'
        root_cb.lines += [assign(run_script_var, function('find_program', [[run_script]], {'required': True}))]

        # Add the targets
        processing = []
        processed = {}
        name_map = {}

        def extract_tgt(tgt: T.Union[ConverterTarget, ConverterCustomTarget, CustomTargetReference]) -> IdNode:
            tgt_name = None
            if isinstance(tgt, (ConverterTarget, ConverterCustomTarget)):
                tgt_name = tgt.name
            elif isinstance(tgt, CustomTargetReference):
                tgt_name = tgt.ctgt.name
            assert(tgt_name is not None and tgt_name in processed)
            res_var = processed[tgt_name]['tgt']
            return id_node(res_var) if res_var else None

        def detect_cycle(tgt: T.Union[ConverterTarget, ConverterCustomTarget]) -> None:
            if tgt.name in processing:
                raise CMakeException('Cycle in CMake inputs/dependencies detected')
            processing.append(tgt.name)

        def resolve_ctgt_ref(ref: CustomTargetReference) -> BaseNode:
            tgt_var = extract_tgt(ref)
            if len(ref.ctgt.outputs) == 1:
                return tgt_var
            else:
                return indexed(tgt_var, ref.index)

        def process_target(tgt: ConverterTarget):
            detect_cycle(tgt)

            # First handle inter target dependencies
            link_with = []
            objec_libs = []  # type: T.List[IdNode]
            sources = []
            generated = []
            generated_filenames = []
            custom_targets = []
            dependencies = []
            for i in tgt.link_with:
                assert(isinstance(i, ConverterTarget))
                if i.name not in processed:
                    process_target(i)
                link_with += [extract_tgt(i)]
            for i in tgt.object_libs:
                assert(isinstance(i, ConverterTarget))
                if i.name not in processed:
                    process_target(i)
                objec_libs += [extract_tgt(i)]
            for i in tgt.depends:
                if not isinstance(i, ConverterCustomTarget):
                    continue
                if i.name not in processed:
                    process_custom_target(i)
                dependencies += [extract_tgt(i)]

            # Generate the source list and handle generated sources
            for i in tgt.sources + tgt.generated:
                if isinstance(i, CustomTargetReference):
                    if i.ctgt.name not in processed:
                        process_custom_target(i.ctgt)
                    generated += [resolve_ctgt_ref(i)]
                    generated_filenames += [i.filename()]
                    if i.ctgt not in custom_targets:
                        custom_targets += [i.ctgt]
                else:
                    sources += [i]

            # Add all header files from all used custom targets. This
            # ensures that all custom targets are built before any
            # sources of the current target are compiled and thus all
            # header files are present. This step is necessary because
            # CMake always ensures that a custom target is executed
            # before another target if at least one output is used.
            for i in custom_targets:
                for j in i.outputs:
                    if not is_header(j) or j in generated_filenames:
                        continue

                    generated += [resolve_ctgt_ref(i.get_ref(j))]
                    generated_filenames += [j]

            # Determine the meson function to use for the build target
            tgt_func = tgt.meson_func()
            if not tgt_func:
                raise CMakeException('Unknown target type "{}"'.format(tgt.type))

            # Determine the variable names
            inc_var = '{}_inc'.format(tgt.name)
            dir_var = '{}_dir'.format(tgt.name)
            sys_var = '{}_sys'.format(tgt.name)
            src_var = '{}_src'.format(tgt.name)
            dep_var = '{}_dep'.format(tgt.name)
            tgt_var = tgt.name

            # Generate target kwargs
            tgt_kwargs = {
                'build_by_default': tgt.install,
                'link_args': tgt.link_flags + tgt.link_libraries,
                'link_with': link_with,
                'include_directories': id_node(inc_var),
                'install': tgt.install,
                'install_dir': tgt.install_dir,
                'override_options': tgt.override_options,
                'objects': [method(x, 'extract_all_objects') for x in objec_libs],
            }

            # Handle compiler args
            for key, val in tgt.compile_opts.items():
                tgt_kwargs['{}_args'.format(key)] = val

            # Handle -fPCI, etc
            if tgt_func == 'executable':
                tgt_kwargs['pie'] = tgt.pie
            elif tgt_func == 'static_library':
                tgt_kwargs['pic'] = tgt.pie

            # declare_dependency kwargs
            dep_kwargs = {
                'link_args': tgt.link_flags + tgt.link_libraries,
                'link_with': id_node(tgt_var),
                'compile_args': tgt.public_compile_opts,
                'include_directories': id_node(inc_var),
            }

            if dependencies:
                generated += dependencies

            # Generate the function nodes
            dir_node = assign(dir_var, function('include_directories', tgt.includes))
            sys_node = assign(sys_var, function('include_directories', tgt.sys_includes, {'is_system': True}))
            inc_node = assign(inc_var, array([id_node(dir_var), id_node(sys_var)]))
            node_list = [dir_node, sys_node, inc_node]
            if tgt_func == 'header_only':
                del dep_kwargs['link_with']
                dep_node = assign(dep_var, function('declare_dependency', kwargs=dep_kwargs))
                node_list += [dep_node]
                src_var = None
                tgt_var = None
            else:
                src_node = assign(src_var, function('files', sources))
                tgt_node = assign(tgt_var, function(tgt_func, [tgt_var, [id_node(src_var)] + generated], tgt_kwargs))
                node_list += [src_node, tgt_node]
                if tgt_func in ['static_library', 'shared_library']:
                    dep_node = assign(dep_var, function('declare_dependency', kwargs=dep_kwargs))
                    node_list += [dep_node]
                else:
                    dep_var = None

            # Add the nodes to the ast
            root_cb.lines += node_list
            processed[tgt.name] = {'inc': inc_var, 'src': src_var, 'dep': dep_var, 'tgt': tgt_var, 'func': tgt_func}
            name_map[tgt.cmake_name] = tgt.name

        def process_custom_target(tgt: ConverterCustomTarget) -> None:
            # CMake allows to specify multiple commands in a custom target.
            # To map this to meson, a helper script is used to execute all
            # commands in order. This additionally allows setting the working
            # directory.

            detect_cycle(tgt)
            tgt_var = tgt.name  # type: str

            def resolve_source(x: T.Any) -> T.Any:
                if isinstance(x, ConverterTarget):
                    if x.name not in processed:
                        process_target(x)
                    return extract_tgt(x)
                if isinstance(x, ConverterCustomTarget):
                    if x.name not in processed:
                        process_custom_target(x)
                    return extract_tgt(x)
                elif isinstance(x, CustomTargetReference):
                    if x.ctgt.name not in processed:
                        process_custom_target(x.ctgt)
                    return resolve_ctgt_ref(x)
                else:
                    return x

            # Generate the command list
            command = []
            command += [id_node(run_script_var)]
            command += ['-o', '@OUTPUT@']
            if tgt.original_outputs:
                command += ['-O'] + tgt.original_outputs
            command += ['-d', tgt.working_dir]

            # Generate the commands. Subcommands are separated by ';;;'
            for cmd in tgt.command:
                command += [resolve_source(x) for x in cmd] + [';;;']

            tgt_kwargs = {
                'input': [resolve_source(x) for x in tgt.inputs],
                'output': tgt.outputs,
                'command': command,
                'depends': [resolve_source(x) for x in tgt.depends],
            }

            root_cb.lines += [assign(tgt_var, function('custom_target', [tgt.name], tgt_kwargs))]
            processed[tgt.name] = {'inc': None, 'src': None, 'dep': None, 'tgt': tgt_var, 'func': 'custom_target'}
            name_map[tgt.cmake_name] = tgt.name

        # Now generate the target function calls
        for i in self.custom_targets:
            if i.name not in processed:
                process_custom_target(i)
        for i in self.targets:
            if i.name not in processed:
                process_target(i)

        self.generated_targets = processed
        self.internal_name_map = name_map
        return root_cb