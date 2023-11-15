def get_availability_zone(vm_):
    """
    Return the availability zone to use
    """
    avz = config.get_cloud_config_value(
        "availability_zone", vm_, __opts__, search_global=False
    )

    if avz is None:
        return None

    zones = list_availability_zones(vm_)

    # Validate user-specified AZ
    if avz not in zones:
        raise SaltCloudException(
            "The specified availability zone isn't valid in this region: "
            "{}\n".format(avz)
        )

    # check specified AZ is available
    elif zones[avz] != "available":
        raise SaltCloudException(
            "The specified availability zone isn't currently available: "
            "{}\n".format(avz)
        )

    return avz