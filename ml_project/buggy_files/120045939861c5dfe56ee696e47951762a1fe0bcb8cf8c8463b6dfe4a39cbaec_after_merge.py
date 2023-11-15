    def get_license_name(self, SourceRecord):
        license = self.get_license(SourceRecord)
        if not license:
            return None
        return license.license_name