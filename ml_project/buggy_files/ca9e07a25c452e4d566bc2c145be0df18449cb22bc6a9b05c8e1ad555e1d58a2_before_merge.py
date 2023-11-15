    def getFileInfo(self, name, pathname):

        try:
            size = os.path.getsize(pathname)
            info = metadata.detect(pathname)

            if info:

                # Sometimes the duration (time) or the bitrate of the file is unknown
                if info["time"] is None or info["bitrate"] is None:
                    fileinfo = (name, size, None, None)
                else:
                    bitrateinfo = (int(info["bitrate"]), int(info["vbr"]))
                    fileinfo = (name, size, bitrateinfo, int(info["time"]))
            else:
                fileinfo = (name, size, None, None)

            return fileinfo

        except Exception as errtuple:
            message = _("Scanning File Error: %(error)s Path: %(path)s") % {'error': errtuple, 'path': pathname}
            self.logMessage(message)
            displayTraceback(sys.exc_info()[2])