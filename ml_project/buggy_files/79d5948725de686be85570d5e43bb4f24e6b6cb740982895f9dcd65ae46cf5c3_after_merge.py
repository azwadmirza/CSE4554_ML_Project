    def verify_node(self,
                    network_middleware,
                    certificate_filepath: str = None,
                    force: bool = False,
                    registry: BaseContractRegistry = None,
                    ) -> bool:
        """
        Three things happening here:

        * Verify that the stamp matches the address (raises InvalidNode is it's not valid,
          or WrongMode if it's a federated mode and being verified as a decentralized node)

        * Verify the interface signature (raises InvalidNode if not valid)

        * Connect to the node, make sure that it's up, and that the signature and address we
          checked are the same ones this node is using now. (raises InvalidNode if not valid;
          also emits a specific warning depending on which check failed).

        """

        if force:
            self.verified_interface = False
            self.verified_node = False
            self.verified_stamp = False
            self.verified_worker = False

        if self.verified_node:
            return True

        if not registry and not self.federated_only:  # TODO: # 466
            self.log.debug("No registry provided for decentralized stranger node verification - "
                           "on-chain Staking verification will not be performed.")

        # This is both the stamp's client signature and interface metadata check; May raise InvalidNode
        self.validate_metadata(registry=registry)

        # The node's metadata is valid; let's be sure the interface is in order.
        if not certificate_filepath:
            if self.certificate_filepath is CERTIFICATE_NOT_SAVED:
                raise TypeError("We haven't saved a certificate for this node yet.")
            else:
                certificate_filepath = self.certificate_filepath

        response_data = network_middleware.node_information(host=self.rest_interface.host,
                                                            port=self.rest_interface.port,
                                                            certificate_filepath=certificate_filepath)

        version, node_bytes = self.version_splitter(response_data, return_remainder=True)
        node_details = self.internal_splitter(node_bytes)
        # TODO: #589 - check timestamp here.

        verifying_keys_match = node_details['verifying_key'] == self.public_keys(SigningPower)
        encrypting_keys_match = node_details['encrypting_key'] == self.public_keys(DecryptingPower)
        addresses_match = node_details['public_address'] == self.canonical_public_address
        evidence_matches = node_details['decentralized_identity_evidence'] == self.__decentralized_identity_evidence

        if not all((encrypting_keys_match, verifying_keys_match, addresses_match, evidence_matches)):
            # Failure
            if not addresses_match:
                self.log.warn("Wallet address swapped out.  It appears that someone is trying to defraud this node.")
            if not verifying_keys_match:
                self.log.warn("Verifying key swapped out.  It appears that someone is impersonating this node.")

            # TODO: #355 - Optional reporting.
            raise self.InvalidNode("Wrong cryptographic material for this node - something fishy going on.")

        else:
            # Success
            self.verified_node = True