    def getFileInfo(self, name, pathname):

        try:
            audio = None
            size = os.stat(pathname).st_size

            if size > 0:
                try:
                    audio = taglib.File(pathname)
                except IOError:
                    pass

            if audio is not None:
                bitrateinfo = (int(audio.bitrate), False)  # Second argument used to be VBR (variable bitrate)
                fileinfo = (name, size, bitrateinfo, int(audio.length))
            else:
                fileinfo = (name, size, None, None)

            return fileinfo

        except Exception as errtuple:
            message = _("Error while scanning file %(path)s: %(error)s") % {'path': pathname, 'error': errtuple}
            self.logMessage(message)
            displayTraceback(sys.exc_info()[2])