def retrieve(click_config,

             # API Options
             provider_uri, network, registry_filepath, checksum_address, dev, config_file, discovery_port,
             teacher_uri, min_stake,

             # Other
             label, policy_encrypting_key, alice_verifying_key, message_kit):
    """
    Obtain plaintext from encrypted data, if access was granted.
    """

    ### Setup ###
    _setup_emitter(click_config)

    bob_config = _get_bob_config(click_config, dev, provider_uri, network, registry_filepath, checksum_address,
                                 config_file, discovery_port)
    #############

    BOB = actions.make_cli_character(character_config=bob_config,
                                     click_config=click_config,
                                     dev=dev,
                                     teacher_uri=teacher_uri,
                                     min_stake=min_stake)

    # Validate
    if not all((label, policy_encrypting_key, alice_verifying_key, message_kit)):
        input_specification, output_specification = BOB.control.get_specifications(interface_name='retrieve')
        required_fields = ', '.join(input_specification)
        raise click.BadArgumentUsage(f'{required_fields} are required flags to retrieve')

    # Request
    bob_request_data = {
        'label': label,
        'policy_encrypting_key': policy_encrypting_key,
        'alice_verifying_key': alice_verifying_key,
        'message_kit': message_kit,
    }

    response = BOB.controller.retrieve(request=bob_request_data)
    return response