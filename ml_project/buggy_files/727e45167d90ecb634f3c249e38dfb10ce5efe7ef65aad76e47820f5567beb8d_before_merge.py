    def get_license(self, SourceRecord):
        license_id = SourceRecord.license_id
        if license_id not in self.licenses:
            LicenseRecord = self.source.get_class(License)
            license = self.source.session.query(LicenseRecord).get(license_id)
            self.licenses[license_id] = license
        return self.licenses[license_id]