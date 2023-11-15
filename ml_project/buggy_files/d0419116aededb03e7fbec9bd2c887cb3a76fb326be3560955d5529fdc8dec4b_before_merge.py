    def node_metadata_exchange():

        # If these nodes already have the same fleet state, no exchange is necessary.
        learner_fleet_state = request.args.get('fleet')
        if learner_fleet_state == this_node.known_nodes.checksum:
            log.debug("Learner already knew fleet state {}; doing nothing.".format(learner_fleet_state))
            headers = {'Content-Type': 'application/octet-stream'}
            payload = this_node.known_nodes.snapshot() + bytes(FLEET_STATES_MATCH)
            signature = this_node.stamp(payload)
            return Response(bytes(signature) + payload, headers=headers)

        sprouts = _node_class.batch_from_bytes(request.data)

        for node in sprouts:
            this_node.remember_node(node)

        # TODO: What's the right status code here?  202?  Different if we already knew about the node(s)?
        return all_known_nodes()