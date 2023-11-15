    def checkNameSize(self, getinfo=True):
        if not self.info or getinfo:
            self.logDebug("File info (BEFORE): %s" % self.info)
            self.info.update(self.getInfo(self.pyfile.url, self.html))
            self.logDebug("File info (AFTER): %s"  % self.info)

        try:
            url  = self.info['url'].strip()
            name = self.info['name'].strip()
            if name and name != url:
                self.pyfile.name = name

        except Exception:
            pass

        try:
            folder = self.info['folder'] = self.pyfile.name

        except Exception:
            pass

        self.logDebug("File name: %s"   % self.pyfile.name,
                      "File folder: %s" % self.pyfile.name)