def list_nodes(conn=None, call=None):
    """
    Return a list of the VMs that are on the provider
    """
    if call == "action":
        raise SaltCloudSystemExit(
            "The list_nodes function must be called with -f or --function."
        )

    if not conn:
        conn = get_conn()  # pylint: disable=E0602

    nodes = conn.list_nodes()
    ret = {}
    for node in nodes:
        ret[node.name] = {
            "id": node.id,
            "image": node.image,
            "name": node.name,
            "private_ips": node.private_ips,
            "public_ips": node.public_ips,
            "size": node.size,
            "state": node_state(node.state),
        }
    return ret