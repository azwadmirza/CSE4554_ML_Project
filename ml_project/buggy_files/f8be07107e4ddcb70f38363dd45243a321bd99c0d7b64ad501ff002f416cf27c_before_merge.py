    def validate_metadata(self,
                          accept_federated_only: bool = False,
                          verify_staking: bool = True):

        # Verify the interface signature
        if not self.verified_interface:
            self.validate_interface()

        # Verify the identity evidence
        if self.verified_stamp:
            return

        # Offline check of valid stamp signature by worker
        try:
            self.validate_worker(verify_staking=verify_staking)
        except self.WrongMode:
            if not accept_federated_only:
                raise