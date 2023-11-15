def make_client(instance):
    """
    Build an AdminClient that will be added as "admin"
    field of `instance`.

    :param instance: an instance of ClientManager
    :returns: an instance of AdminClient
    """
    endpoint = instance.get_endpoint('admin')
    client = AdminClient(
        session=instance.session,
        endpoint=endpoint,
        namespace=instance.namespace)
    return client