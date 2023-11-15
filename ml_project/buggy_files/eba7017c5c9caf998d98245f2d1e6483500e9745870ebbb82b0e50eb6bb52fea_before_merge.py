    def outputs_older_than_script_or_notebook(self):
        """return output that's older than script, i.e. script has changed"""
        path = self.rule.script or self.rule.notebook
        if not path:
            return
        assert os.path.exists(path)  # to make sure lstat works
        script_mtime = os.lstat(path).st_mtime
        for f in self.expanded_output:
            if f.exists:
                if not f.is_newer(script_mtime):
                    yield f