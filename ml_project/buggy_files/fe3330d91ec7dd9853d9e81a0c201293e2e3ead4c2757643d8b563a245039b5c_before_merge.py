    def sendNumSharedFoldersFiles(self):
        """
        Send number of files in buddy shares if only buddies can
        download, and buddy-shares are enabled.
        """
        conf = self.config.sections

        if conf["transfers"]["enablebuddyshares"] and conf["transfers"]["friendsonly"]:
            shared_db = "bsharedfiles"
        else:
            shared_db = "sharedfiles"

        sharedfolders = len(conf["transfers"][shared_db])
        sharedfiles = sum([len(x) for x in list(conf["transfers"][shared_db].values())])
        self.queue.put(slskmessages.SharedFoldersFiles(sharedfolders, sharedfiles))