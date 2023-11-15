    def globalize(self):
        """
        Reverse the effect of localize().
        """
        try:
            with open(os.path.join(self.dirPath, '.original')) as f:
                return self.__class__(*json.loads(f.read()))
        except IOError as e:
            if e.errno == errno.ENOENT:
                if self._runningOnWorker():
                    log.warn("Can't globalize module %r.", self)
                return self
            else:
                raise