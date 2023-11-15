    def __init__(self,

                 # Ursula
                 rest_host: str,
                 rest_port: int,
                 domains: Set = None,  # For now, serving and learning domains will be the same.
                 certificate: Certificate = None,
                 certificate_filepath: str = None,
                 db_filepath: str = None,
                 is_me: bool = True,
                 interface_signature=None,
                 timestamp=None,
                 availability_check: bool = True,
                 prune_datastore: bool = True,
                 metrics_port: int = None,

                 # Blockchain
                 decentralized_identity_evidence: bytes = constants.NOT_SIGNED,
                 checksum_address: str = None,
                 worker_address: str = None,  # TODO: deprecate, and rename to "checksum_address"
                 work_tracker: WorkTracker = None,
                 start_working_now: bool = True,
                 client_password: str = None,

                 # Character
                 abort_on_learning_error: bool = False,
                 federated_only: bool = False,
                 start_learning_now: bool = None,
                 crypto_power=None,
                 tls_curve: EllipticCurve = None,
                 known_nodes: Iterable = None,

                 **character_kwargs
                 ) -> None:

        #
        # Character
        #

        if domains is None:
            # TODO: Move defaults to configuration, Off character.
            from nucypher.config.node import CharacterConfiguration
            domains = {CharacterConfiguration.DEFAULT_DOMAIN}

        if is_me:
            # If we're federated only, we assume that all other nodes in our domain are as well.
            self.set_federated_mode(federated_only)

        Character.__init__(self,
                           is_me=is_me,
                           checksum_address=checksum_address,
                           start_learning_now=False,  # Handled later in this function to avoid race condition
                           federated_only=self._federated_only_instances,  # TODO: 'Ursula' object has no attribute '_federated_only_instances' if an is_me Ursula is not inited prior to this moment  NRN
                           crypto_power=crypto_power,
                           abort_on_learning_error=abort_on_learning_error,
                           known_nodes=known_nodes,
                           domains=domains,
                           known_node_class=Ursula,
                           **character_kwargs)

        if is_me:

            # In-Memory TreasureMap tracking
            self._stored_treasure_maps = dict()

            # Learner
            self._start_learning_now = start_learning_now

            # Self-Health Checks
            self._availability_check = availability_check
            self._availability_tracker = AvailabilityTracker(ursula=self)

            # Arrangement Pruning
            self.__pruning_task = None
            self._prune_datastore = prune_datastore
            self._arrangement_pruning_task = LoopingCall(f=self.__prune_arrangements)

            # Prometheus / Metrics
            self._metrics_port = metrics_port

        #
        # Ursula the Decentralized Worker (Self)
        #

        if is_me and not federated_only:  # TODO: #429

            # Prepare a TransactingPower from worker node's transacting keys
            self.transacting_power = TransactingPower(account=worker_address,
                                                      password=client_password,
                                                      signer=self.signer,
                                                      cache=True)
            self._crypto_power.consume_power_up(self.transacting_power)

            # Use this power to substantiate the stamp
            self.substantiate_stamp()
            self.log.debug(f"Created decentralized identity evidence: {self.decentralized_identity_evidence[:10].hex()}")
            decentralized_identity_evidence = self.decentralized_identity_evidence

            Worker.__init__(self,
                            is_me=is_me,
                            registry=self.registry,
                            checksum_address=checksum_address,
                            worker_address=worker_address,
                            work_tracker=work_tracker,
                            start_working_now=start_working_now)

        if not crypto_power or (TLSHostingPower not in crypto_power):

            #
            # Development Ursula
            #

            if is_me:
                self.suspicious_activities_witnessed = {'vladimirs': [],
                                                        'bad_treasure_maps': [],
                                                        'freeriders': []}

                # REST Server (Ephemeral Self-Ursula)
                rest_app, datastore = make_rest_app(
                    this_node=self,
                    db_filepath=db_filepath,
                    serving_domains=domains,
                )

                # TLSHostingPower (Ephemeral Powers and Private Keys)
                tls_hosting_keypair = HostingKeypair(curve=tls_curve, host=rest_host,
                                                     checksum_address=self.checksum_address)
                tls_hosting_power = TLSHostingPower(keypair=tls_hosting_keypair, host=rest_host)
                self.rest_server = ProxyRESTServer(rest_host=rest_host, rest_port=rest_port,
                                                   rest_app=rest_app, datastore=datastore,
                                                   hosting_power=tls_hosting_power)

            #
            # Stranger-Ursula
            #

            else:

                # TLSHostingPower
                if certificate or certificate_filepath:
                    tls_hosting_power = TLSHostingPower(host=rest_host,
                                                        public_certificate_filepath=certificate_filepath,
                                                        public_certificate=certificate)
                else:
                    tls_hosting_keypair = HostingKeypair(curve=tls_curve, host=rest_host, generate_certificate=False)
                    tls_hosting_power = TLSHostingPower(host=rest_host, keypair=tls_hosting_keypair)

                # REST Server
                # Unless the caller passed a crypto power we'll make our own TLSHostingPower for this stranger.
                self.rest_server = ProxyRESTServer(
                    rest_host=rest_host,
                    rest_port=rest_port,
                    hosting_power=tls_hosting_power
                )

            # OK - Now we have a ProxyRestServer and a TLSHostingPower for some Ursula
            self._crypto_power.consume_power_up(tls_hosting_power)  # Consume!

        #
        # Teacher (Verifiable Node)
        #

        certificate_filepath = self._crypto_power.power_ups(TLSHostingPower).keypair.certificate_filepath
        certificate = self._crypto_power.power_ups(TLSHostingPower).keypair.certificate
        Teacher.__init__(self,
                         domains=domains,
                         certificate=certificate,
                         certificate_filepath=certificate_filepath,
                         interface_signature=interface_signature,
                         timestamp=timestamp,
                         decentralized_identity_evidence=decentralized_identity_evidence)

        if is_me:
            self.known_nodes.record_fleet_state(additional_nodes_to_track=[self])  # Initial Impression

            message = "THIS IS YOU: {}: {}".format(self.__class__.__name__, self)
            self.log.info(message)
            self.log.info(self.banner.format(self.nickname))
        else:
            message = "Initialized Stranger {} | {}".format(self.__class__.__name__, self)
            self.log.debug(message)