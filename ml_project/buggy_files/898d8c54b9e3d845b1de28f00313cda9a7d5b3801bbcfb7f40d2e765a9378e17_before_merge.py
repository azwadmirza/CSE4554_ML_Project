    def decrypt(self, pyfile):
        self.prepare()
        self.check_info()  #@TODO: Remove in 0.4.10

        if self.direct_dl:
            self.log_debug(_("Looking for direct download link..."))
            self.handle_direct(pyfile)

            if self.link or self.links or self.urls or self.packages:
                self.log_info(_("Direct download link detected"))
            else:
                self.log_info(_("Direct download link not found"))

        if not (self.link or self.links or self.urls or self.packages):
            self.preload()

            self.links = self.get_links() or list()

            if hasattr(self, 'PAGES_PATTERN') and hasattr(self, 'loadPage'):
                self.handle_pages(pyfile)

            self.log_debug("Package has %d links" % len(self.links))

        if self.link:
            self.urls.append(self.link)

        if self.links:
            name = folder = pyfile.name
            self.packages.append((name, self.links, folder))