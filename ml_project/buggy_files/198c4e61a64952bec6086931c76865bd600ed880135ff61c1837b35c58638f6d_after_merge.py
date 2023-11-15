    def prep_preexec_fn(self, kwargs, pipeline_group=None):
        """Prepares the 'preexec_fn' keyword argument"""
        if not ON_POSIX:
            return
        if not builtins.__xonsh_env__.get('XONSH_INTERACTIVE'):
            return
        if pipeline_group is None:
            xonsh_preexec_fn = no_pg_xonsh_preexec_fn
        else:
            def xonsh_preexec_fn():
                """Preexec function bound to a pipeline group."""
                os.setpgid(0, pipeline_group)
                signal.signal(signal.SIGTSTP, default_signal_pauser)
        kwargs['preexec_fn'] = xonsh_preexec_fn