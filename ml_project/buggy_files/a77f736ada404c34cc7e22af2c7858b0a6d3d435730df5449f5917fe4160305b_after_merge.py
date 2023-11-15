    def from_configuration_file(cls, filepath: str = None, **overrides) -> 'NodeConfiguration':
        """Initialize a NodeConfiguration from a JSON file."""

        from nucypher.config.storages import NodeStorage
        node_storage_subclasses = {storage._name: storage for storage in NodeStorage.__subclasses__()}

        if filepath is None:
            filepath = cls.DEFAULT_CONFIG_FILE_LOCATION

        # Read from disk
        payload = cls._read_configuration_file(filepath=filepath)

        # Sanity check
        try:
            checksum_address = payload['checksum_public_address']
        except KeyError:
            raise cls.ConfigurationError(f"No checksum address specified in configuration file {filepath}")
        else:
            if not eth_utils.is_checksum_address(checksum_address):
                raise cls.ConfigurationError(f"Address: '{checksum_address}', specified in {filepath} is not a valid checksum address.")

        # Initialize NodeStorage subclass from file (sub-configuration)
        storage_payload = payload['node_storage']
        storage_type = storage_payload[NodeStorage._TYPE_LABEL]
        storage_class = node_storage_subclasses[storage_type]
        node_storage = storage_class.from_payload(payload=storage_payload,
                                                  federated_only=payload['federated_only'],
                                                  serializer=cls.NODE_SERIALIZER,
                                                  deserializer=cls.NODE_DESERIALIZER)

        # Deserialize domains to UTF-8 bytestrings
        domains = set(domain.encode() for domain in payload['domains'])
        payload.update(dict(node_storage=node_storage, domains=domains))

        # Filter out Nones from overrides to detect, well, overrides
        overrides = {k: v for k, v in overrides.items() if v is not None}

        # Instantiate from merged params
        node_configuration = cls(**{**payload, **overrides})

        return node_configuration