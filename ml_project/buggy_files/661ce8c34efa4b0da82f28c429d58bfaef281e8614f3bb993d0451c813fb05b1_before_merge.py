def has_lldp(module):
    output = run_commands(module, ['show lldp'])

    is_lldp_enable = False
    if len(output) > 0 and "LLDP is not enabled" not in output[0]:
        is_lldp_enable = True

    return is_lldp_enable