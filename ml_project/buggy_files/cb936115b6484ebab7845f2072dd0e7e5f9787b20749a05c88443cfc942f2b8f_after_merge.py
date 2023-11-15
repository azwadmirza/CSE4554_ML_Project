def get_external_ip_from_default_teacher(network: str,
                                         federated_only: bool = False,
                                         registry: Optional[BaseContractRegistry] = None,
                                         log: Logger = IP_DETECTION_LOGGER
                                         ) -> Union[str, None]:

    # Prevents circular import
    from nucypher.characters.lawful import Ursula

    if federated_only and registry:
        raise ValueError('Federated mode must not be true if registry is provided.')
    base_error = 'Cannot determine IP using default teacher'
    try:
        top_teacher_url = RestMiddleware.TEACHER_NODES[network][0]
    except IndexError:
        log.debug(f'{base_error}: No teacher available for network "{network}".')
        return
    except KeyError:
        log.debug(f'{base_error}: Unknown network "{network}".')
        return

    ####
    # TODO: Clean this mess #1481 (Federated Mode)
    node_storage = LocalFileBasedNodeStorage(federated_only=federated_only)
    Ursula.set_cert_storage_function(node_storage.store_node_certificate)
    Ursula.set_federated_mode(federated_only)
    #####

    try:
        teacher = Ursula.from_teacher_uri(teacher_uri=top_teacher_url,
                                          federated_only=federated_only,
                                          min_stake=0)  # TODO: Handle customized min stake here.
    except NodeSeemsToBeDown:
        # Teacher is unreachable.  Move on.
        return

    # TODO: Pass registry here to verify stake (not essential here since it's a hardcoded node)
    result = _request_from_node(teacher=teacher)
    return result