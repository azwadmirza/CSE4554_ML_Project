    def getFilesIndex(self, mtimes, oldmtimes, newsharedfiles, yieldcall=None, progress=None):

        wordindex = defaultdict(list)
        fileindex = []
        index = 0
        count = len(mtimes)
        lastpercent = 0.0

        for directory in mtimes:

            virtualdir = self.real2virtual(directory)
            count += 1

            if progress:
                # Truncate the percentage to two decimal places to avoid sending data to the GUI thread too often
                percent = float("%.2f" % (float(count) / len(mtimes) * 0.75))

                if percent > lastpercent and percent <= 1.0:
                    GLib.idle_add(progress.set_fraction, percent)
                    lastpercent = percent

            if self.hiddenCheck({'dir': directory}):
                continue

            for j in newsharedfiles[virtualdir]:
                file = j[0]
                fileindex.append((virtualdir + '\\' + file,) + j[1:])

                # Collect words from filenames for Search index (prevent duplicates with set)
                words = set((virtualdir + " " + file).translate(self.translatepunctuation).lower().split())

                for k in words:
                    wordindex[k].append(index)

                index += 1

            if yieldcall is not None:
                yieldcall()

        return wordindex, fileindex