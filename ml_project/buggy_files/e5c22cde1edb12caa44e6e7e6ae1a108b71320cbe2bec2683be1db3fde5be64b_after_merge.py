    def _fix_cwd(self):
        """Check if the cwd changed out from under us."""
        env = builtins.__xonsh_env__
        try:
            cwd = os.getcwd()
        except (FileNotFoundError, OSError):
            cwd = None
        if cwd is None:
            # directory has been deleted out from under us, most likely
            pwd = env.get('PWD', None)
            if pwd is None:
                # we have no idea where we are
                env['PWD'] = '<invalid directory>'
            elif os.path.isdir(pwd):
                # unclear why os.getcwd() failed. do nothing.
                pass
            else:
                # OK PWD is really gone.
                msg = '{UNDERLINE_INTENSE_WHITE}{BACKGROUND_INTENSE_BLACK}'
                msg += "xonsh: working directory does not exist: " + pwd
                msg += '{NO_COLOR}'
                self.print_color(msg, file=sys.stderr)
        elif 'PWD' not in env:
            # $PWD is missing from env, recreate it
            env['PWD'] = cwd
        elif os.path.realpath(cwd) != os.path.realpath(env['PWD']):
            # The working directory has changed without updating $PWD, fix this
            old = env['PWD']
            env['PWD'] = cwd
            env['OLDPWD'] = old
            events.on_chdir.fire(olddir=old, newdir=cwd)