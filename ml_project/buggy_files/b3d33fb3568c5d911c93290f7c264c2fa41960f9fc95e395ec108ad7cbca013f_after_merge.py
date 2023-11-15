    def from_seed_and_stake_info(cls,
                                 seed_uri: str,
                                 federated_only: bool,
                                 minimum_stake: int = 0,
                                 registry: BaseContractRegistry = None,
                                 network_middleware: RestMiddleware = None,
                                 *args,
                                 **kwargs
                                 ) -> 'Ursula':

        if network_middleware is None:
            network_middleware = RestMiddleware()

        #
        # WARNING: xxx Poison xxx
        # Let's learn what we can about the ... "seednode".
        #

        # Parse node URI
        host, port, checksum_address = parse_node_uri(seed_uri)

        # Fetch the hosts TLS certificate and read the common name
        certificate = network_middleware.get_certificate(host=host, port=port)
        real_host = certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

        # Create a temporary certificate storage area
        temp_node_storage = ForgetfulNodeStorage(federated_only=federated_only)
        temp_certificate_filepath = temp_node_storage.store_node_certificate(certificate=certificate)

        # Load the host as a potential seed node
        potential_seed_node = cls.from_rest_url(
            registry=registry,
            host=real_host,
            port=port,
            network_middleware=network_middleware,
            certificate_filepath=temp_certificate_filepath,
            federated_only=federated_only,
            *args,
            **kwargs
        )

        # Check the node's stake (optional)
        if minimum_stake > 0 and not federated_only:
            staking_agent = ContractAgency.get_agent(StakingEscrowAgent, registry=registry)
            seednode_stake = staking_agent.get_locked_tokens(staker_address=checksum_address)
            if seednode_stake < minimum_stake:
                raise Learner.NotATeacher(f"{checksum_address} is staking less then the specified minimum stake value ({minimum_stake}).")

        # Verify the node's TLS certificate
        try:
            potential_seed_node.verify_node(network_middleware=network_middleware,
                                            registry=registry,
                                            certificate_filepath=temp_certificate_filepath)
        except potential_seed_node.InvalidNode:
            # TODO: What if our seed node fails verification?
            raise

        # OK - everyone get out
        temp_node_storage.forget()
        return potential_seed_node