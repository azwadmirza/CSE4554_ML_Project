    def outputs_older_than_script_or_notebook(self):
        """return output that's older than script, i.e. script has changed"""
        path = self.rule.script or self.rule.notebook
        if not path:
            return
        if self.rule.basedir:
            # needed if rule is included from another subdirectory
            path = os.path.relpath(os.path.join(self.rule.basedir, path))
        assert os.path.exists(path), "cannot find {0}".format(path)
        script_mtime = os.lstat(path).st_mtime
        for f in self.expanded_output:
            if f.exists:
                if not f.is_newer(script_mtime):
                    yield f