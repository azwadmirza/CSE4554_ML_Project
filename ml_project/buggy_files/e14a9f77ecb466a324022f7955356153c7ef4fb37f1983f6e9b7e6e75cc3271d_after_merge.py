    def to_dict(self):
        archives_size = 0
        for k in self.archives:
            archives_size += self.archives[k]["size"]
        d = {
            "CreationDate": self.st.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "LastInventoryDate": self.st.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "NumberOfArchives": len(self.archives),
            "SizeInBytes": archives_size,
            "VaultARN": self.arn,
            "VaultName": self.vault_name,
        }
        return d