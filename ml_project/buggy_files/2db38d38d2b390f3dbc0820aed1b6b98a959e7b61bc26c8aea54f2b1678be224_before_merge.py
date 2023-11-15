    def _exec_command(command, slot_info, events):
        host = slot_info.hostname
        local_rank = slot_info.local_rank
        result = rsh(driver_addresses, key, settings, host, command, env, local_rank, False, events)
        return result, time.time()