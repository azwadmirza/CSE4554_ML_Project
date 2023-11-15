def has_lldp(module):
    config = get_config(module, flags=['| section lldp'])

    is_lldp_enable = False
    if "no lldp run" not in config:
        is_lldp_enable = True

    return is_lldp_enable