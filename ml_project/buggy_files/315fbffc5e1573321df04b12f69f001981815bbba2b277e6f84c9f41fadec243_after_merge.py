    def getFilesStreams(self, mtimes, oldmtimes, oldstreams, newsharedfiles, rebuild=False, yieldcall=None):

        streams = {}

        for folder in mtimes:

            virtualdir = self.real2virtual(folder)

            if self.hiddenCheck({'dir': folder}):
                continue

            if not rebuild and folder in oldmtimes:
                if mtimes[folder] == oldmtimes[folder]:
                    if os.path.exists(folder):
                        # No change
                        try:
                            streams[virtualdir] = oldstreams[virtualdir]
                            continue
                        except KeyError:
                            log.addwarning(_("Inconsistent cache for '%(vdir)s', rebuilding '%(dir)s'") % {
                                'vdir': virtualdir,
                                'dir': folder
                            })
                    else:
                        log.adddebug(_("Dropping missing directory %(dir)s") % {'dir': folder})
                        continue

            streams[virtualdir] = self.getDirStream(newsharedfiles[virtualdir])

            if yieldcall is not None:
                yieldcall()

        return streams