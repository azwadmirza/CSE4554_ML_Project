            def learn_about_announced_nodes():

                try:
                    certificate_filepath = forgetful_node_storage.store_node_certificate(
                        certificate=node.certificate)

                    node.verify_node(this_node.network_middleware,
                                     registry=this_node.registry,
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