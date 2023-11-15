    def node_metadata_exchange():
        # If these nodes already have the same fleet state, no exchange is necessary.

        learner_fleet_state = request.args.get('fleet')
        if learner_fleet_state == this_node.known_nodes.checksum:
            log.debug("Learner already knew fleet state {}; doing nothing.".format(learner_fleet_state))
            headers = {'Content-Type': 'application/octet-stream'}
            payload = this_node.known_nodes.snapshot() + bytes(FLEET_STATES_MATCH)
            signature = this_node.stamp(payload)
            return Response(bytes(signature) + payload, headers=headers)

        nodes = _node_class.batch_from_bytes(request.data,
                                             registry=this_node.registry,
                                             federated_only=this_node.federated_only)  # TODO: 466

        # TODO: This logic is basically repeated in learn_from_teacher_node and remember_node.
        # Let's find a better way.  #555
        for node in nodes:
            if not set(serving_domains).intersection(set(node.serving_domains)):
                continue  # This node is not serving any of our domains.

            if node in this_node.known_nodes:
                if node.timestamp <= this_node.known_nodes[node.checksum_address].timestamp:
                    continue

            @crosstown_traffic()
            def learn_about_announced_nodes():

                try:
                    certificate_filepath = forgetful_node_storage.store_node_certificate(
                        certificate=node.certificate)

                    node.verify_node(this_node.network_middleware,
                                     accept_federated_only=this_node.federated_only,  # TODO: 466
                                     certificate_filepath=certificate_filepath)

                # Suspicion
                except node.SuspiciousActivity as e:
                    # TODO: Include data about caller?
                    # TODO: Account for possibility that stamp, rather than interface, was bad.
                    # TODO: Maybe also record the bytes representation separately to disk?
                    message = f"Suspicious Activity about {node}: {str(e)}.  Announced via REST."
                    log.warn(message)
                    this_node.suspicious_activities_witnessed['vladimirs'].append(node)
                except NodeSeemsToBeDown as e:
                    # This is a rather odd situation - this node *just* contacted us and asked to be verified.  Where'd it go?  Maybe a NAT problem?
                    log.info(f"Node announced itself to us just now, but seems to be down: {node}.  Response was {e}.")
                    log.debug(f"Phantom node certificate: {node.certificate}")
                # Async Sentinel
                except Exception as e:
                    log.critical(f"This exception really needs to be handled differently: {e}")
                    raise

                # Believable
                else:
                    log.info("Learned about previously unknown node: {}".format(node))
                    this_node.remember_node(node)
                    # TODO: Record new fleet state

                # Cleanup
                finally:
                    forgetful_node_storage.forget()

        # TODO: What's the right status code here?  202?  Different if we already knew about the node?
        return all_known_nodes()