    def remember_node(self, node, force_verification_check=False, record_fleet_state=True):

        if node == self:  # No need to remember self.
            return False

        # First, determine if this is an outdated representation of an already known node.
        # TODO: #1032
        with suppress(KeyError):
            already_known_node = self.known_nodes[node.checksum_address]
            if not node.timestamp > already_known_node.timestamp:
                self.log.debug("Skipping already known node {}".format(already_known_node))
                # This node is already known.  We can safely return.
                return False

        try:
            stranger_certificate = node.certificate
        except AttributeError:
            # Whoops, we got an Alice, Bob, or someone...
            raise self.NotATeacher(f"{node.__class__.__name__} does not have a certificate and cannot be remembered.")

        # Store node's certificate - It has been seen.
        certificate_filepath = self.node_storage.store_node_certificate(certificate=stranger_certificate)

        # In some cases (seed nodes or other temp stored certs),
        # this will update the filepath from the temp location to this one.
        node.certificate_filepath = certificate_filepath
        self.log.info(f"Saved TLS certificate for {node.nickname}: {certificate_filepath}")

        try:
            node.verify_node(force=force_verification_check,
                             network_middleware=self.network_middleware,
                             accept_federated_only=self.federated_only,  # TODO: 466 - move federated-only up to Learner?
                             )
        except SSLError:
            return False  # TODO: Bucket this node as having bad TLS info - maybe it's an update that hasn't fully propagated?

        except NodeSeemsToBeDown:
            self.log.info("No Response while trying to verify node {}|{}".format(node.rest_interface, node))
            return False  # TODO: Bucket this node as "ghost" or something: somebody else knows about it, but we can't get to it.

        listeners = self._learning_listeners.pop(node.checksum_address, tuple())
        address = node.checksum_address

        self.known_nodes[address] = node

        if self.save_metadata:
            self.node_storage.store_node_metadata(node=node)

        self.log.info("Remembering {} ({}), popping {} listeners.".format(node.nickname, node.checksum_address, len(listeners)))
        for listener in listeners:
            listener.add(address)
        self._node_ids_to_learn_about_immediately.discard(address)

        if record_fleet_state:
            self.known_nodes.record_fleet_state()

        return node