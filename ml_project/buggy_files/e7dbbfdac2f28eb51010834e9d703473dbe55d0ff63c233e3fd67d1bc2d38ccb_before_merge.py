    def localize(self):
        """
        Check if this module was saved as a resource. If it was, return a new module descriptor
        that points to a local copy of that resource. Should only be called on a worker node.

        :rtype: toil.resource.Resource
        """
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
            return self.__class__(dirPath=resource.localDirPath, name=self.name,
                                  extension=self.extension)