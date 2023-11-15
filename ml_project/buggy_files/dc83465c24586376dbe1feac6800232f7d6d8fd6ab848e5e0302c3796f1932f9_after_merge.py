def get_address_info_from_redis_helper(redis_address,
                                       node_ip_address,
                                       redis_password=None):
    redis_ip_address, redis_port = redis_address.split(":")
    # Get node table from global state accessor.
    global_state = ray.state.GlobalState()
    global_state._initialize_global_state(redis_address, redis_password)
    client_table = global_state.node_table()
    if len(client_table) == 0:
        raise RuntimeError(
            "Redis has started but no raylets have registered yet.")

    relevant_client = None
    for client_info in client_table:
        client_node_ip_address = client_info["NodeManagerAddress"]
        if (client_node_ip_address == node_ip_address
                or (client_node_ip_address == "127.0.0.1"
                    and redis_ip_address == get_node_ip_address())
                or client_node_ip_address == redis_ip_address):
            relevant_client = client_info
            break
    if relevant_client is None:
        raise RuntimeError(
            f"This node has an IP address of {node_ip_address}, and Ray "
            "expects this IP address to be either the Redis address or one of"
            f" the Raylet addresses. Connected to Redis at {redis_address} and"
            " found raylets at "
            f"{', '.join(c['NodeManagerAddress'] for c in client_table)} but "
            f"none of these match this node's IP {node_ip_address}. Are any of"
            " these actually a different IP address for the same node?"
            "You might need to provide --node-ip-address to specify the IP "
            "address that the head should use when sending to this node.")

    return {
        "object_store_address": relevant_client["ObjectStoreSocketName"],
        "raylet_socket_name": relevant_client["RayletSocketName"],
        "node_manager_port": relevant_client["NodeManagerPort"],
    }