    def run_command_impl(self, node, args, kwargs, in_builddir=False):
        if len(args) < 1:
            raise InterpreterException('Not enough arguments')
        cmd = args[0]
        cargs = args[1:]
        capture = kwargs.get('capture', True)
        srcdir = self.environment.get_source_dir()
        builddir = self.environment.get_build_dir()

        check = kwargs.get('check', False)
        if not isinstance(check, bool):
            raise InterpreterException('Check must be boolean.')

        m = 'must be a string, or the output of find_program(), files() '\
            'or configure_file(), or a compiler object; not {!r}'
        if isinstance(cmd, ExternalProgramHolder):
            cmd = cmd.held_object
            if isinstance(cmd, build.Executable):
                progname = node.args.arguments[0].value
                msg = 'Program {!r} was overridden with the compiled executable {!r}'\
                      ' and therefore cannot be used during configuration'
                raise InterpreterException(msg.format(progname, cmd.description()))
        elif isinstance(cmd, CompilerHolder):
            cmd = cmd.compiler.get_exelist()[0]
            prog = ExternalProgram(cmd, silent=True)
            if not prog.found():
                raise InterpreterException('Program {!r} not found '
                                           'or not executable'.format(cmd))
            cmd = prog
        else:
            if isinstance(cmd, mesonlib.File):
                cmd = cmd.absolute_path(srcdir, builddir)
            elif not isinstance(cmd, str):
                raise InterpreterException('First argument ' + m.format(cmd))
            # Prefer scripts in the current source directory
            search_dir = os.path.join(srcdir, self.subdir)
            prog = ExternalProgram(cmd, silent=True, search_dir=search_dir)
            if not prog.found():
                raise InterpreterException('Program or command {!r} not found '
                                           'or not executable'.format(cmd))
            cmd = prog
        try:
            cmd_path = os.path.relpath(cmd.get_path(), start=srcdir)
        except ValueError:
            # On Windows a relative path can't be evaluated for
            # paths on two different drives (i.e. c:\foo and f:\bar).
            # The only thing left to is is to use the original absolute
            # path.
            cmd_path = cmd.get_path()
        if not cmd_path.startswith('..') and cmd_path not in self.build_def_files:
            self.build_def_files.append(cmd_path)
        expanded_args = []
        for a in listify(cargs):
            if isinstance(a, str):
                expanded_args.append(a)
            elif isinstance(a, mesonlib.File):
                expanded_args.append(a.absolute_path(srcdir, builddir))
            elif isinstance(a, ExternalProgramHolder):
                expanded_args.append(a.held_object.get_path())
            else:
                raise InterpreterException('Arguments ' + m.format(a))
        for a in expanded_args:
            if not os.path.isabs(a):
                a = os.path.join(builddir if in_builddir else srcdir, self.subdir, a)
            if os.path.isfile(a):
                a = os.path.relpath(a, start=srcdir)
                if not a.startswith('..'):
                    if a not in self.build_def_files:
                        self.build_def_files.append(a)
        return RunProcess(cmd, expanded_args, srcdir, builddir, self.subdir,
                          self.environment.get_build_command() + ['introspect'],
                          in_builddir=in_builddir, check=check, capture=capture)