    def getFilesStreams(self, mtimes, oldmtimes, oldstreams, newsharedfiles, rebuild=False, yieldcall=None):

        streams = {}

        for directory in list(mtimes.keys()):

            virtualdir = self.real2virtual(directory)

            if self.hiddenCheck({'dir': directory}):
                continue

            if not rebuild and directory in oldmtimes:
                if mtimes[directory] == oldmtimes[directory]:
                    if os.path.exists(directory):
                        # No change
                        try:
                            streams[virtualdir] = oldstreams[virtualdir]
                            continue
                        except KeyError:
                            log.addwarning(_("Inconsistent cache for '%(vdir)s', rebuilding '%(dir)s'") % {
                                'vdir': virtualdir,
                                'dir': directory
                            })
                    else:
                        log.adddebug(_("Dropping missing directory %(dir)s") % {'dir': directory})
                        continue

            streams[virtualdir] = self.getDirStream(newsharedfiles[virtualdir])

            if yieldcall is not None:
                yieldcall()

        return streams