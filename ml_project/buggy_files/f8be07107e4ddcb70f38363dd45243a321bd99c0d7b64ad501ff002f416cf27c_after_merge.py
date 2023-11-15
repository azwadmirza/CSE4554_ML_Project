    def validate_metadata(self, registry: BaseContractRegistry = None):

        # Verify the interface signature
        if not self.verified_interface:
            self.validate_interface()

        # Verify the identity evidence
        if self.verified_stamp:
            return

        # Offline check of valid stamp signature by worker
        try:
            self.validate_worker(registry=registry)
        except self.WrongMode:
            if bool(registry):
                raise