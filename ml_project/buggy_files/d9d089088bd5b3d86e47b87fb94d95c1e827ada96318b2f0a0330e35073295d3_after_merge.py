def _check_ami(config):
    """Provide helpful message for missing ImageId for node configuration."""

    _set_config_info(head_ami_src="config", workers_ami_src="config")

    region = config["provider"]["region"]
    default_ami = DEFAULT_AMI.get(region)
    if not default_ami:
        # If we do not provide a default AMI for the given region, noop.
        return

    head_ami = config["head_node"].get("ImageId", "").lower()
    if head_ami in ["", "latest_dlami"]:
        config["head_node"]["ImageId"] = default_ami
        _set_config_info(head_ami_src="dlami")

    worker_ami = config["worker_nodes"].get("ImageId", "").lower()
    if worker_ami in ["", "latest_dlami"]:
        config["worker_nodes"]["ImageId"] = default_ami
        _set_config_info(workers_ami_src="dlami")