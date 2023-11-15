    def rescandirs(self, shared, oldmtimes, oldfiles, sharedfilesstreams, yieldfunction, progress=None, name="", rebuild=False):
        """
        Check for modified or new files via OS's last mtime on a directory,
        or, if rebuild is True, all directories
        """

        # returns dict in format:  { Directory : mtime, ... }
        shared_directories = [x[1] for x in shared]

        GLib.idle_add(progress.set_text, _("Checking for changes"))
        GLib.idle_add(progress.show)
        GLib.idle_add(progress.set_fraction, 0)

        self.logMessage(_("%(num)s directories found before rescan, rebuilding...") % {"num": len(oldmtimes)})

        newmtimes = self.getDirsMtimes(shared_directories, yieldfunction)

        GLib.idle_add(progress.set_text, _("Scanning %s") % name)

        # Get list of files
        # returns dict in format { Directory : { File : metadata, ... }, ... }
        newsharedfiles = self.getFilesList(newmtimes, oldmtimes, oldfiles, yieldfunction, progress, rebuild)

        # Pack shares data
        # returns dict in format { Directory : hex string of files+metadata, ... }
        GLib.idle_add(progress.set_text, _("Building Database"))

        newsharedfilesstreams = self.getFilesStreams(newmtimes, oldmtimes, sharedfilesstreams, newsharedfiles, rebuild, yieldfunction)

        # Update Search Index
        # newwordindex is a dict in format {word: [num, num, ..], ... } with num matching
        # keys in newfileindex
        # newfileindex is a dict in format { num: (path, size, (bitrate, vbr), length), ... }
        GLib.idle_add(progress.set_text, _("Building Index"))

        GLib.idle_add(progress.set_fraction, 0.0)

        newwordindex, newfileindex = self.getFilesIndex(newmtimes, oldmtimes, shared_directories, newsharedfiles, yieldfunction, progress)

        GLib.idle_add(progress.set_fraction, 1.0)

        self.logMessage(_("%(num)s directories found after rescan") % {"num": len(newmtimes)})

        return newsharedfiles, newsharedfilesstreams, newwordindex, newfileindex, newmtimes