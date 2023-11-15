    def _AddVersionResource(self, fileName):
        try:
            from win32verstamp import stamp
        except:
            print("*** WARNING *** unable to create version resource")
            print("install pywin32 extensions first")
            return
        versionInfo = VersionInfo(self.metadata.version,
                comments = self.metadata.long_description,
                description = self.metadata.description,
                company = self.metadata.author,
                product = self.metadata.name)
        stamp(fileName, versionInfo)