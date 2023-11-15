def _sge_info(queue):
    """Returns machine information for an sge job scheduler.
    """
    qhost_out = subprocess.check_output(["qhost", "-q", "-xml"]).decode()
    qstat_queue = ["-q", queue] if queue and "," not in queue else []
    qstat_out = subprocess.check_output(["qstat", "-f", "-xml"] + qstat_queue).decode()
    slot_info = _sge_get_slots(qstat_out)
    mem_info = _sge_get_mem(qhost_out, queue)
    machine_keys = slot_info.keys()
    #num_cpus_vec = [slot_info[x]["slots_total"] for x in machine_keys]
    #mem_vec = [mem_info[x]["mem_total"] for x in machine_keys]
    mem_per_slot = [mem_info[x]["mem_total"] / float(slot_info[x]["slots_total"]) for x in machine_keys]
    min_ratio_index = mem_per_slot.index(median_left(mem_per_slot))
    mem_info[machine_keys[min_ratio_index]]["mem_total"]
    return [{"cores": slot_info[machine_keys[min_ratio_index]]["slots_total"],
             "memory": mem_info[machine_keys[min_ratio_index]]["mem_total"],
             "name": "sge_machine"}]