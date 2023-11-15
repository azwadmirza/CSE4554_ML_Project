    def unpack_env_kwarg(self, kwargs):
        envlist = kwargs.get('env', EnvironmentVariablesHolder())
        if isinstance(envlist, EnvironmentVariablesHolder):
            env = envlist.held_object
        else:
            if not isinstance(envlist, list):
                envlist = [envlist]
            env = {}
            for e in envlist:
                if '=' not in e:
                    raise InterpreterException('Env var definition must be of type key=val.')
                (k, val) = e.split('=', 1)
                k = k.strip()
                val = val.strip()
                if ' ' in k:
                    raise InterpreterException('Env var key must not have spaces in it.')
                env[k] = val
        return env