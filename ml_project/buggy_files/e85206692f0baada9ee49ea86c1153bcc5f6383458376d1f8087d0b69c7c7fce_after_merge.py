    def _load_start_paths(self):
        " Start the Read-Eval-Print Loop. "
        if self._startup_paths:
            for path in self._startup_paths:
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        code = compile(f.read(), path, 'exec')
                        six.exec_(code, self.get_globals(), self.get_locals())
                else:
                    output = self.app.output
                    output.write('WARNING | File not found: {}\n\n'.format(path))