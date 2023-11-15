def make_cli_character(character_config,
                       click_config,
                       unlock_keyring: bool = True,
                       teacher_uri: str = None,
                       min_stake: int = 0,
                       load_preferred_teachers: bool = True,
                       **config_args):

    emitter = click_config.emitter

    #
    # Pre-Init
    #

    # Handle Keyring

    if unlock_keyring:
        character_config.attach_keyring()
        unlock_nucypher_keyring(emitter,
                                character_configuration=character_config,
                                password=get_nucypher_password(confirm=False))

    # Handle Teachers
    teacher_nodes = list()
    if load_preferred_teachers:
        teacher_nodes = load_seednodes(emitter,
                                       teacher_uris=[teacher_uri] if teacher_uri else None,
                                       min_stake=min_stake,
                                       federated_only=character_config.federated_only,
                                       network_domains=character_config.domains,
                                       network_middleware=character_config.network_middleware,
                                       registry=character_config.registry)

    #
    # Character Init
    #

    # Produce Character
    try:
        CHARACTER = character_config(known_nodes=teacher_nodes,
                                     network_middleware=character_config.network_middleware,
                                     **config_args)
    except CryptoError:
        raise character_config.keyring.AuthenticationFailed("Failed to unlock keyring. "
                                                            "Are you sure you provided the correct password?")
    #
    # Post-Init
    #

    if CHARACTER.controller is not NO_CONTROL_PROTOCOL:
        CHARACTER.controller.emitter = emitter  # TODO: set it on object creation? Or not set at all?

    # Federated
    if character_config.federated_only:
        emitter.message("WARNING: Running in Federated mode", color='yellow')

    return CHARACTER