def unlock_nucypher_keyring(emitter, password: str, character_configuration: CharacterConfiguration):
    emitter.message(f'Decrypting {character_configuration._NAME} keyring...', color='yellow')
    if character_configuration.dev_mode:
        return True  # Dev accounts are always unlocked

    # NuCypher
    try:
        character_configuration.attach_keyring()
        character_configuration.keyring.unlock(password=password)  # Takes ~3 seconds, ~1GB Ram
    except CryptoError:
        raise character_configuration.keyring.AuthenticationFailed