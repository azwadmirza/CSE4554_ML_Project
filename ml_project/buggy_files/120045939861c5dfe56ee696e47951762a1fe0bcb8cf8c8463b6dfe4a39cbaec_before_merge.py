    def get_license_name(self, SourceRecord):
        license = self.get_license(SourceRecord)
        return license.license_name