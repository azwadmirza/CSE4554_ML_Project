    def getFilesList(self, mtimes, oldmtimes, oldlist, yieldcall=None, progress=None, rebuild=False):
        """ Get a list of files with their filelength, bitrate and track length in seconds """

        list = {}
        count = 0
        lastpercent = 0.0

        for folder in mtimes:

            try:
                count += 1

                if progress:
                    # Truncate the percentage to two decimal places to avoid sending data to the GUI thread too often
                    percent = float("%.2f" % (float(count) / len(mtimes) * 0.75))

                    if percent > lastpercent and percent <= 1.0:
                        GLib.idle_add(progress.set_fraction, percent)
                        lastpercent = percent

                if self.hiddenCheck({'dir': folder}):
                    continue

                if not rebuild and folder in oldmtimes:
                    if mtimes[folder] == oldmtimes[folder]:
                        if os.path.exists(folder):
                            try:
                                virtualdir = self.real2virtual(folder)
                                list[virtualdir] = oldlist[virtualdir]
                                continue
                            except KeyError:
                                log.adddebug(_("Inconsistent cache for '%(vdir)s', rebuilding '%(dir)s'") % {
                                    'vdir': virtualdir,
                                    'dir': folder
                                })
                        else:
                            log.adddebug(_("Dropping missing directory %(dir)s") % {'dir': folder})
                            continue

                virtualdir = self.real2virtual(folder)
                list[virtualdir] = []

                for entry in os.scandir(folder):

                    if entry.is_file():
                        filename = entry.name

                        if self.hiddenCheck({'dir': folder, 'file': filename}):
                            continue

                        # Get the metadata of the file via mutagen
                        data = self.getFileInfo(filename, entry.path)
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