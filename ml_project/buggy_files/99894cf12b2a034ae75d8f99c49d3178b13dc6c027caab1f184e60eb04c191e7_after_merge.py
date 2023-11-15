def _exec_command_fn(driver_addresses, key, settings, env):
    def _exec_command(command, slot_info, events):
        host = slot_info.hostname
        local_rank = slot_info.local_rank
        verbose = settings.verbose
        result = rsh(driver_addresses, key, host, command, env, local_rank, verbose, False, events)
        return result, time.time()
    return _exec_command