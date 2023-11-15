    def addToShared(self, name):
        """ Add a file to the normal shares database """

        config = self.config.sections
        if not config["transfers"]["sharedownloaddir"]:
            return

        shared = config["transfers"]["sharedfiles"]
        sharedstreams = config["transfers"]["sharedfilesstreams"]
        wordindex = config["transfers"]["wordindex"]
        fileindex = config["transfers"]["fileindex"]

        shareddirs = [path for _name, path in config["transfers"]["shared"]]
        shareddirs.append(config["transfers"]["downloaddir"])

        sharedmtimes = config["transfers"]["sharedmtimes"]

        dir = str(os.path.expanduser(os.path.dirname(name)))
        vdir = self.real2virtual(dir)
        file = str(os.path.basename(name))

        shared[vdir] = shared.get(vdir, [])

        if file not in [i[0] for i in shared[vdir]]:
            fileinfo = self.getFileInfo(file, name)
            shared[vdir] = shared[vdir] + [fileinfo]
            sharedstreams[vdir] = self.getDirStream(shared[vdir])
            words = self.getIndexWords(vdir, file, shareddirs)
            self.addToIndex(wordindex, fileindex, words, vdir, fileinfo)
            sharedmtimes[vdir] = os.path.getmtime(dir)
            self.newnormalshares = True

        if config["transfers"]["enablebuddyshares"]:
            self.addToBuddyShared(name)

        self.config.writeShares()