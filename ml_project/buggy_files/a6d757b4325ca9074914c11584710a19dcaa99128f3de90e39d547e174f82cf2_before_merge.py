    def validate_worker(self, verify_staking: bool = True) -> None:

        # Federated
        if self.federated_only:
            message = "This node cannot be verified in this manner, " \
                      "but is OK to use in federated mode if you "    \
                      "have reason to believe it is trustworthy."
            raise self.WrongMode(message)

        # Decentralized
        else:

            if self.__decentralized_identity_evidence is NOT_SIGNED:
                raise self.StampNotSigned

            # Off-chain signature verification
            if not self._stamp_has_valid_signature_by_worker():
                message = f"Invalid signature {self.__decentralized_identity_evidence.hex()} " \
                          f"from worker {self.worker_address} for stamp {bytes(self.stamp).hex()} "
                raise self.InvalidWorkerSignature(message)

            # On-chain staking check
            if verify_staking:
                if not self._worker_is_bonded_to_staker():  # <-- Blockchain CALL
                    message = f"Worker {self.worker_address} is not bonded to staker {self.checksum_address}"
                    raise self.DetachedWorker(message)

                if self._staker_is_really_staking():  # <-- Blockchain CALL
                    self.verified_worker = True
                else:
                    raise self.NotStaking(f"Staker {self.checksum_address} is not staking")

            self.verified_stamp = True