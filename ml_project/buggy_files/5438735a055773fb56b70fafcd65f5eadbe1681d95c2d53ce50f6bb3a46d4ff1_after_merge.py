    def get_license_description(self, SourceRecord):
        license = self.get_license(SourceRecord)
        if not license:
            return None
        return license.license_description