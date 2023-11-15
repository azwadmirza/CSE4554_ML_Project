    def run(self, *, pipeline_group=None):
        """Launches the subprocess and returns the object."""
        kwargs = {n: getattr(self, n) for n in self.kwnames}
        self.prep_env(kwargs)
        self.prep_preexec_fn(kwargs, pipeline_group=pipeline_group)
        if callable(self.alias):
            if 'preexec_fn' in kwargs:
                kwargs.pop('preexec_fn')
            p = self.cls(self.alias, self.cmd, **kwargs)
        else:
            p = self._run_binary(kwargs)
        p.spec = self
        p.last_in_pipeline = self.last_in_pipeline
        p.captured_stdout = self.captured_stdout
        p.captured_stderr = self.captured_stderr
        return p