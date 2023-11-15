    def create(cls, jobStore, leaderPath):
        """
        Saves the content of the file or directory at the given path to the given job store
        and returns a resource object representing that content for the purpose of obtaining it
        again at a generic, public URL. This method should be invoked on the leader node.

        :param toil.jobStores.abstractJobStore.AbstractJobStore jobStore:

        :param str leaderPath:

        :rtype: Resource
        """
        pathHash = cls._pathHash(leaderPath)
        contentHash = hashlib.md5()
        # noinspection PyProtectedMember
        with cls._load(leaderPath) as src:
            with jobStore.writeSharedFileStream(sharedFileName=pathHash, isProtected=False) as dst:
                userScript = src.read()
                contentHash.update(userScript)
                dst.write(userScript)
        return cls(name=os.path.basename(leaderPath),
                   pathHash=pathHash,
                   url=jobStore.getSharedPublicUrl(sharedFileName=pathHash),
                   contentHash=contentHash.hexdigest())