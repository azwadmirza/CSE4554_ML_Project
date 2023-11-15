def _reorder_bits(job_data):
    """Temporary fix for ibmq backends.

    For every ran circuit, get reordering information from qobj
    and apply reordering on result.

    Args:
        job_data (dict): dict with the bare contents of the API.get_job request.

    Raises:
            JobError: raised if the creg sizes don't add up in result header.
    """
    for circuit_result in job_data['qasms']:
        if 'metadata' in circuit_result:
            circ = circuit_result['metadata'].get('compiled_circuit')
        else:
            logger.warning('result object missing metadata for reordering'
                           ' bits: bits may be out of order')
            return
        # device_qubit -> device_clbit (how it should have been)
        measure_dict = {op['qubits'][0]: op['memory'][0]
                        for op in circ['operations']
                        if op['name'] == 'measure'}
        counts_dict_new = {}
        for item in circuit_result['data']['counts'].items():
            # fix clbit ordering to what it should have been
            bits = list(item[0])
            bits.reverse()  # lsb in 0th position
            count = item[1]
            reordered_bits = list('x' * len(bits))
            for device_clbit, bit in enumerate(bits):
                if device_clbit in measure_dict:
                    correct_device_clbit = measure_dict[device_clbit]
                    reordered_bits[correct_device_clbit] = bit
            reordered_bits.reverse()

            # only keep the clbits specified by circuit, not everything on device
            num_clbits = circ['header']['memory_slots']
            compact_key = reordered_bits[-num_clbits:]
            compact_key = "".join([b if b != 'x' else '0'
                                   for b in compact_key])

            # insert spaces to signify different classical registers
            cregs = circ['header']['creg_sizes']
            if sum([creg[1] for creg in cregs]) != num_clbits:
                raise JobError("creg sizes don't add up in result header.")
            creg_begin_pos = []
            creg_end_pos = []
            acc = 0
            for creg in reversed(cregs):
                creg_size = creg[1]
                creg_begin_pos.append(acc)
                creg_end_pos.append(acc + creg_size)
                acc += creg_size
            compact_key = " ".join([compact_key[creg_begin_pos[i]:creg_end_pos[i]]
                                    for i in range(len(cregs))])

            # marginalize over unwanted measured qubits
            if compact_key not in counts_dict_new:
                counts_dict_new[compact_key] = count
            else:
                counts_dict_new[compact_key] += count

        circuit_result['data']['counts'] = counts_dict_new