    def getFilesIndex(self, mtimes, oldmtimes, shareddirs, newsharedfiles, yieldcall=None, progress=None):

        wordindex = defaultdict(list)
        fileindex = {}
        index = 0
        count = 0

        for directory in mtimes:

            virtualdir = self.real2virtual(directory)

            if progress:
                percent = float(count) / len(mtimes)
                if percent <= 1.0:
                    GLib.idle_add(progress.set_fraction, percent)

            count += 1

            if self.hiddenCheck({'dir': directory}):
                continue

            for j in newsharedfiles[virtualdir]:
                indexes = self.getIndexWords(virtualdir, j[0], shareddirs)

                for k in indexes:
                    wordindex[k].append(index)

                fileindex[str(index)] = ((virtualdir + '\\' + j[0]), ) + j[1:]
                index += 1

            if yieldcall is not None:
                yieldcall()

        return wordindex, fileindex