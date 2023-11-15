    def initialize_options(self):
        self.all = True
        self._clean_me = []
        self._clean_trees = []
        for root, dirs, files in list(os.walk('pandas')):
            for f in files:
                if os.path.splitext(f)[-1] in ('.pyc', '.so', '.o',
                                               '.pyd', '.c'):
                    self._clean_me.append(pjoin(root, f))
            for d in dirs:
                if d == '__pycache__':
                    self._clean_trees.append(pjoin(root, d))

        for d in ('build',):
            if os.path.exists(d):
                self._clean_trees.append(d)