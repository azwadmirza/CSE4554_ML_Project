    def getDirsMtimes(self, dirs, yieldcall=None):

        list = {}

        for folder in dirs:

            folder = os.path.expanduser(folder.replace("//", "/"))

            if self.hiddenCheck({'dir': folder}):
                continue

            try:
                mtime = os.path.getmtime(folder)
            except OSError as errtuple:
                message = _("Scanning Directory Error: %(error)s Path: %(path)s") % {'error': errtuple, 'path': folder}
                print(str(message))
                self.logMessage(message)
                continue

            list[folder] = mtime

            try:
                for entry in os.scandir(folder):

                    if entry.is_dir():

                        path = os.path.join(folder, entry.path.split("/")[-1])

                        try:
                            mtime = os.path.getmtime(path)
                        except OSError as errtuple:
                            islink = False
                            try:
                                islink = os.path.islink(path)
                            except OSError as errtuple2:
                                print(errtuple2)

                            if islink:
                                message = _("Scanning Error: Broken link to directory: \"%(link)s\" from Path: \"%(path)s\". Repair or remove this link.") % {
                                    'link': os.readlink(path),
                                    'path': path
                                }
                            else:
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