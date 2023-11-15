    def learn_from_teacher_node(self, eager=True):
        """
        Sends a request to node_url to find out about known nodes.
        """
        self._learning_round += 1

        try:
            current_teacher = self.current_teacher_node()
        except self.NotEnoughTeachers as e:
            self.log.warn("Can't learn right now: {}".format(e.args[0]))
            return

        if Teacher in self.__class__.__bases__:
            announce_nodes = [self]
        else:
            announce_nodes = None

        unresponsive_nodes = set()

        #
        # Request
        #

        try:

            response = self.network_middleware.get_nodes_via_rest(node=current_teacher,
                                                                  nodes_i_need=self._node_ids_to_learn_about_immediately,
                                                                  announce_nodes=announce_nodes,
                                                                  fleet_checksum=self.known_nodes.checksum)
        except NodeSeemsToBeDown as e:
            unresponsive_nodes.add(current_teacher)
            self.log.info("Bad Response from teacher: {}:{}.".format(current_teacher, e))
            return

        finally:
            self.cycle_teacher_node()

        # Before we parse the response, let's handle some edge cases.
        if response.status_code == 204:
            # In this case, this node knows about no other nodes.  Hopefully we've taught it something.
            if response.content == b"":
                return NO_KNOWN_NODES
            # In the other case - where the status code is 204 but the repsonse isn't blank - we'll keep parsing.
            # It's possible that our fleet states match, and we'll check for that later.

        elif response.status_code != 200:
            self.log.info("Bad response from teacher {}: {} - {}".format(current_teacher, response, response.content))
            return

        #
        # Deserialize
        #

        try:
            signature, node_payload = signature_splitter(response.content, return_remainder=True)
        except BytestringSplittingError as e:
            self.log.warn("No signature prepended to Teacher {} payload: {}".format(current_teacher, response.content))
            return

        try:
            self.verify_from(current_teacher, node_payload, signature=signature)
        except current_teacher.InvalidSignature:
            # TODO: What to do if the teacher improperly signed the node payload?
            raise

        # End edge case handling.
        fleet_state_checksum_bytes, fleet_state_updated_bytes, node_payload = FleetStateTracker.snapshot_splitter(
            node_payload,
            return_remainder=True)

        current_teacher.last_seen = maya.now()
        # TODO: This is weird - let's get a stranger FleetState going.
        checksum = fleet_state_checksum_bytes.hex()

        # TODO: This doesn't make sense - a decentralized node can still learn about a federated-only node.
        from nucypher.characters.lawful import Ursula
        if constant_or_bytes(node_payload) is FLEET_STATES_MATCH:
            current_teacher.update_snapshot(checksum=checksum,
                                            updated=maya.MayaDT(int.from_bytes(fleet_state_updated_bytes, byteorder="big")),
                                            number_of_known_nodes=len(self.known_nodes))
            return FLEET_STATES_MATCH

        node_list = Ursula.batch_from_bytes(node_payload,
                                            registry=self.registry,
                                            federated_only=self.federated_only)  # TODO: 466

        current_teacher.update_snapshot(checksum=checksum,
                                        updated=maya.MayaDT(int.from_bytes(fleet_state_updated_bytes, byteorder="big")),
                                        number_of_known_nodes=len(node_list))

        new_nodes = []
        for node in node_list:
            if not set(self.learning_domains).intersection(set(node.serving_domains)):
                self.log.debug(f"Teacher {node} is serving {node.serving_domains}, but we're only learning {self.learning_domains}.")
                continue  # This node is not serving any of our domains.

            # First, determine if this is an outdated representation of an already known node.
            # TODO: #1032
            with suppress(KeyError):
                already_known_node = self.known_nodes[node.checksum_address]
                if not node.timestamp > already_known_node.timestamp:
                    self.log.debug("Skipping already known node {}".format(already_known_node))
                    # This node is already known.  We can safely continue to the next.
                    continue

            #
            # Verify Node
            #

            certificate_filepath = self.node_storage.store_node_certificate(certificate=node.certificate)
            try:
                if eager:
                    node.verify_node(self.network_middleware,
                                     registry=self.registry,
                                     certificate_filepath=certificate_filepath)
                    self.log.debug("Verified node: {}".format(node.checksum_address))

                else:
                    node.validate_metadata(registry=self.registry)

            #
            # Report Failure
            #

            except NodeSeemsToBeDown:
                self.log.info(f"Verification Failed - "
                              f"Cannot establish connection to {node}.")

            except node.StampNotSigned:
                self.log.warn(f'Verification Failed - '
                              f'{node} stamp is unsigned.')

            except node.NotStaking:
                self.log.warn(f'Verification Failed - '
                              f'{node} has no active stakes in the current period '
                              f'({self.staking_agent.get_current_period()}')

            except node.InvalidWorkerSignature:
                self.log.warn(f'Verification Failed - '
                              f'{node} has an invalid wallet signature for {node.decentralized_identity_evidence}')

            except node.DetachedWorker:
                self.log.warn(f'Verification Failed - '
                              f'{node} is not bonded to a Staker.')

            except node.InvalidNode:
                self.log.warn(node.invalid_metadata_message.format(node))

            except node.SuspiciousActivity:
                message = f"Suspicious Activity: Discovered node with bad signature: {node}." \
                          f"Propagated by: {current_teacher}"
                self.log.warn(message)

            #
            # Success
            #

            else:
                new = self.remember_node(node, record_fleet_state=False)
                if new:
                    new_nodes.append(node)

        #
        # Continue
        #

        self._adjust_learning(new_nodes)
        learning_round_log_message = "Learning round {}.  Teacher: {} knew about {} nodes, {} were new."
        self.log.info(learning_round_log_message.format(self._learning_round,
                                                        current_teacher,
                                                        len(node_list),
                                                        len(new_nodes)))
        if new_nodes:
            self.known_nodes.record_fleet_state()
            for node in new_nodes:
                self.node_storage.store_node_certificate(certificate=node.certificate)
        return new_nodes