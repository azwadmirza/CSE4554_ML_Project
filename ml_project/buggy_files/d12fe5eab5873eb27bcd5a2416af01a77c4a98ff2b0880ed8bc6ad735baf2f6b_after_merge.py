def make_client(instance):
    """
    Build an AdminClient that will be added as "admin"
    field of `instance`.

    :param instance: an instance of ClientManager
    :returns: an instance of AdminClient
    """
    client = AdminClient(
        **instance.get_process_configuration()
    )
    return client