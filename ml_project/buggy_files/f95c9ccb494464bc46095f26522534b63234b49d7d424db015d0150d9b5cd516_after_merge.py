    def from_bytes(cls,
                   ursula_as_bytes: bytes,
                   version: int = INCLUDED_IN_BYTESTRING,
                   federated_only: bool = False,
                   registry: BaseContractRegistry = None,
                   ) -> 'Ursula':

        if version is INCLUDED_IN_BYTESTRING:
            version, payload = cls.version_splitter(ursula_as_bytes, return_remainder=True)
        else:
            payload = ursula_as_bytes

        # Check version and raise IsFromTheFuture if this node is... you guessed it...
        if version > cls.LEARNER_VERSION:

            # Try to handle failure, even during failure, graceful degradation
            # TODO: #154 - Some auto-updater logic?

            try:
                canonical_address, _ = BytestringSplitter(PUBLIC_ADDRESS_LENGTH)(payload, return_remainder=True)
                checksum_address = to_checksum_address(canonical_address)
                nickname, _ = nickname_from_seed(checksum_address)
                display_name = cls._display_name_template.format(cls.__name__, nickname, checksum_address)
                message = cls.unknown_version_message.format(display_name, version, cls.LEARNER_VERSION)
            except BytestringSplittingError:
                message = cls.really_unknown_version_message.format(version, cls.LEARNER_VERSION)
            raise cls.IsFromTheFuture(message)

        # Version stuff checked out.  Moving on.
        node_info = cls.internal_splitter(payload)

        interface_info = node_info.pop("rest_interface")
        node_info['rest_host'] = interface_info.host
        node_info['rest_port'] = interface_info.port

        node_info['timestamp'] = maya.MayaDT(node_info.pop("timestamp"))
        node_info['checksum_address'] = to_checksum_address(node_info.pop("public_address"))

        domains_vbytes = VariableLengthBytestring.dispense(node_info['domains'])
        node_info['domains'] = set(d.decode('utf-8') for d in domains_vbytes)

        ursula = cls.from_public_keys(federated_only=federated_only, **node_info)
        return ursula