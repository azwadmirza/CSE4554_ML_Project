    def get_license_description(self, SourceRecord):
        license = self.get_license(SourceRecord)
        return license.license_description