    def getFilesList(self, mtimes, oldmtimes, oldlist, yieldcall=None, progress=None, rebuild=False):
        """ Get a list of files with their filelength, bitrate and track length in seconds """

        list = {}
        count = 0

        for folder in mtimes:

            folder = os.path.expanduser(folder)
            virtualdir = self.real2virtual(folder)
            count += 1

            if progress:
                percent = float(count) / len(mtimes)
                if percent <= 1.0:
                    GLib.idle_add(progress.set_fraction, percent)

            if self.hiddenCheck({'dir': folder}):
                continue

            if not rebuild and folder in oldmtimes:
                if mtimes[folder] == oldmtimes[folder]:
                    if os.path.exists(folder):
                        try:
                            list[virtualdir] = oldlist[virtualdir]
                            continue
                        except KeyError:
                            log.addwarning(_("Inconsistent cache for '%(vdir)s', rebuilding '%(dir)s'") % {
                                'vdir': virtualdir,
                                'dir': folder
                            })
                    else:
                        log.adddebug(_("Dropping missing directory %(dir)s") % {'dir': folder})
                        continue

            list[virtualdir] = []

            try:
                for entry in os.scandir(folder):

                    if entry.is_file():
                        filename = entry.path.split("/")[-1]

                        if self.hiddenCheck({'dir': folder, 'file': filename}):
                            continue

                        path = os.path.join(folder, filename)

                        # Get the metadata of the file via mutagen
                        data = self.getFileInfo(filename, path)
                        if data is not None:
                            list[virtualdir].append(data)

                    if yieldcall is not None:
                        yieldcall()
            except OSError as errtuple:
                message = _("Scanning Directory Error: %(error)s Path: %(path)s") % {'error': errtuple, 'path': folder}
                print(str(message))
                self.logMessage(message)
                continue

        return list