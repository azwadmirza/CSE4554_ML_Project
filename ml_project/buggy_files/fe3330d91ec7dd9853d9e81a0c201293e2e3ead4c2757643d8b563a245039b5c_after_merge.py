    def sendNumSharedFoldersFiles(self):
        """
        Send number of files in buddy shares if only buddies can
        download, and buddy-shares are enabled.
        """

        conf = self.config.sections

        if conf["transfers"]["enablebuddyshares"] and conf["transfers"]["friendsonly"]:
            shared_db = "bsharedfiles"
            index_db = "bfileindex"
        else:
            shared_db = "sharedfiles"
            index_db = "fileindex"

        sharedfolders = len(conf["transfers"][shared_db])
        sharedfiles = len(conf["transfers"][index_db])

        self.queue.put(slskmessages.SharedFoldersFiles(sharedfolders, sharedfiles))