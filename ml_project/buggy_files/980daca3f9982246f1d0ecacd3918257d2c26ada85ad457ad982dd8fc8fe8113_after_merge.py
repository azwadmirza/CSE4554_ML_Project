    def getDirsMtimes(self, dirs, yieldcall=None):

        list = {}

        for folder in dirs:

            try:
                if self.hiddenCheck({'dir': folder}):
                    continue

                mtime = os.path.getmtime(folder)
                list[folder] = mtime

                for entry in os.scandir(folder):
                    if entry.is_dir():

                        path = entry.path

                        try:
                            mtime = entry.stat().st_mtime
                        except OSError as errtuple:
                            message = _("Scanning Error: %(error)s Path: %(path)s") % {
                                'error': errtuple,
                                'path': path
                            }

                            print(str(message))
                            self.logMessage(message)
                            continue

                        list[path] = mtime
                        dircontents = self.getDirsMtimes([path])
                        for k in dircontents:
                            list[k] = dircontents[k]

                    if yieldcall is not None:
                        yieldcall()
            except OSError as errtuple:
                message = _("Scanning Directory Error: %(error)s Path: %(path)s") % {'error': errtuple, 'path': folder}
                print(str(message))
                self.logMessage(message)
                continue

        return list