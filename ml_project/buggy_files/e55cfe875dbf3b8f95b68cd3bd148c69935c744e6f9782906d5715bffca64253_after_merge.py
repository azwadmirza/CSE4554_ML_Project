    def rescandirs(self, shared, oldmtimes, oldfiles, sharedfilesstreams, yieldfunction, progress=None, name="", rebuild=False):
        """
        Check for modified or new files via OS's last mtime on a directory,
        or, if rebuild is True, all directories
        """

        GLib.idle_add(progress.set_fraction, 0.0)
        GLib.idle_add(progress.show)

        # returns dict in format:  { Directory : mtime, ... }
        shared_directories = [x[1] for x in shared]

        self.logMessage(_("%(num)s directories found before rescan, rebuilding...") % {"num": len(oldmtimes)})

        newmtimes = self.getDirsMtimes(shared_directories, yieldfunction)

        # Get list of files
        # returns dict in format { Directory : { File : metadata, ... }, ... }
        newsharedfiles = self.getFilesList(newmtimes, oldmtimes, oldfiles, yieldfunction, progress, rebuild)

        # Pack shares data
        # returns dict in format { Directory : hex string of files+metadata, ... }
        newsharedfilesstreams = self.getFilesStreams(newmtimes, oldmtimes, sharedfilesstreams, newsharedfiles, rebuild, yieldfunction)

        # Update Search Index
        # newwordindex is a dict in format {word: [num, num, ..], ... } with num matching
        # keys in newfileindex
        # newfileindex is a dict in format { num: (path, size, (bitrate, vbr), length), ... }
        newwordindex, newfileindex = self.getFilesIndex(newmtimes, oldmtimes, newsharedfiles, yieldfunction, progress)

        self.logMessage(_("%(num)s directories found after rescan") % {"num": len(newmtimes)})

        return newsharedfiles, newsharedfilesstreams, newwordindex, newfileindex, newmtimes