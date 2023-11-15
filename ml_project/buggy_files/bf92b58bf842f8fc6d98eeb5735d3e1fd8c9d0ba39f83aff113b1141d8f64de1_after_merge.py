def get_verification_attributes(connection, module, identity, retries=0, retryDelay=10):
    # Unpredictably get_identity_verification_attributes doesn't include the identity even when we've
    # just registered it. Suspect this is an eventual consistency issue on AWS side.
    # Don't want this complexity exposed users of the module as they'd have to retry to ensure
    # a consistent return from the module.
    # To avoid this we have an internal retry that we use only after registering the identity.
    for attempt in range(0, retries + 1):
        response = call_and_handle_errors(module, connection.get_identity_verification_attributes, Identities=[identity])
        identity_verification = response['VerificationAttributes']
        if identity in identity_verification:
            break
        time.sleep(retryDelay)
    if identity not in identity_verification:
        return None
    return identity_verification[identity]