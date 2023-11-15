    def localize(self):
        """
        Check if this module was saved as a resource. If it was, return a new module descriptor
        that points to a local copy of that resource. Should only be called on a worker node. On
        the leader, this method returns this resource, i.e. self.

        :rtype: toil.resource.Resource
        """
        if self._runningOnWorker():
            log.warn('The localize() method should only be invoked on a worker.')
        resource = Resource.lookup(self._resourcePath)
        if resource is None:
            log.warn("Can't localize module %r", self)
            return self
        else:
            def stash(tmpDirPath):
                # Save the original dirPath such that we can restore it in globalize()
                with open(os.path.join(tmpDirPath, '.original'), 'w') as f:
                    f.write(json.dumps(self))

            resource.download(callback=stash)
            return self.__class__(dirPath=resource.localDirPath, name=self.name)