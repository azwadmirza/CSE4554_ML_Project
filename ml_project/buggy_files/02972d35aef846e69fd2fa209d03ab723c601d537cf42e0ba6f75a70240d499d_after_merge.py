    def to_dict(self):
        d = {
            "Action": "ArchiveRetrieval",
            "ArchiveId": self.archive_id,
            "ArchiveSizeInBytes": 0,
            "ArchiveSHA256TreeHash": None,
            "Completed": False,
            "CreationDate": self.st.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "InventorySizeInBytes": 0,
            "JobDescription": None,
            "JobId": self.job_id,
            "RetrievalByteRange": None,
            "SHA256TreeHash": None,
            "SNSTopic": None,
            "StatusCode": "InProgress",
            "StatusMessage": None,
            "VaultARN": self.arn,
            "Tier": self.tier
        }
        if datetime.datetime.now() > self.et:
            d["Completed"] = True
            d["CompletionDate"] = self.et.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            d["InventorySizeInBytes"] = 10000
            d["StatusCode"] = "Succeeded"
        return d