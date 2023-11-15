    def __call__(self, require):
        if not self.valid:
            raise ConanException("Invalid use of python_requires(%s)" % require)
        try:
            python_req = self._look_for_require(require)
            self._requires.append(python_req)
            return python_req.module
        except NotFoundException:
            raise ConanException('Unable to find python_requires("{}") in remotes'.format(require))