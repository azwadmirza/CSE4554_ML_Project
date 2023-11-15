    def _fix_cwd(self):
        """Check if the cwd changed out from under us."""
        env = builtins.__xonsh_env__
        cwd = os.getcwd()
        if 'PWD' not in env:
            # $PWD is missing from env, recreate it
            env['PWD'] = cwd
        elif os.path.realpath(cwd) != os.path.realpath(env['PWD']):
            # The working directory has changed without updating $PWD, fix this
            old = env['PWD']
            env['PWD'] = cwd
            env['OLDPWD'] = old
            events.on_chdir.fire(olddir=old, newdir=cwd)