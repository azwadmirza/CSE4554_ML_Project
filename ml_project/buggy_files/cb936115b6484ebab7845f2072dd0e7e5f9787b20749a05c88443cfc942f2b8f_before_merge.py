def get_external_ip_from_default_teacher(network: str,
                                         federated_only: bool = False,
                                         log: Logger = IP_DETECTION_LOGGER,
                                         registry: BaseContractRegistry = None
                                         ) -> Union[str, None]:
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
    # TODO: Clean this mess #1481
    node_storage = LocalFileBasedNodeStorage(federated_only=federated_only)
    Ursula.set_cert_storage_function(node_storage.store_node_certificate)
    Ursula.set_federated_mode(federated_only)
    #####

    teacher = Ursula.from_teacher_uri(teacher_uri=top_teacher_url,
                                      federated_only=federated_only,
                                      min_stake=0)  # TODO: Handle customized min stake here.

    # TODO: Pass registry here to verify stake (not essential here since it's a hardcoded node)
    client = NucypherMiddlewareClient()
    try:
        response = client.get(node_or_sprout=teacher, path=f"ping", timeout=2)  # TLS certificate logic within
    except RestMiddleware.UnexpectedResponse:
        # 404, 405, 500, All server response codes handled by will be caught here.
        return  # Default teacher does not support this request - just move on.
    if response.status_code == 200:
        try:
            ip = str(ip_address(response.text))
        except ValueError:
            error = f'Default teacher at {top_teacher_url} returned an invalid IP response; Got {response.text}'
            raise UnknownIPAddress(error)
        log.info(f'Fetched external IP address ({ip}) from default teacher ({top_teacher_url}).')
        return ip
    else:
        log.debug(f'Failed to get external IP from teacher node ({response.status_code})')