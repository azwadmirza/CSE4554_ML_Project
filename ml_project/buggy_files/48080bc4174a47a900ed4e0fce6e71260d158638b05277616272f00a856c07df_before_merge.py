    def lookup(cls, leaderPath):
        """
        Returns a resource object representing a resource created from a file or directory at the
        given path on the leader. This method should be invoked on the worker. The given path
        does not need to refer to an existing file or directory on the worker, it only identifies
        the resource within an instance of toil. This method returns None if no resource for the
        given path exists.

        :rtype: Resource
        """
        pathHash = cls._pathHash(leaderPath)
        try:
            s = os.environ[cls.resourceEnvNamePrefix + pathHash]
        except KeyError:
            log.warn("Can't find resource for leader path '%s'", leaderPath)
            return None
        else:
            self = cls._unpickle(s)
            assert self.pathHash == pathHash
            return self