def _persist_accummulators(accumulators, accumulators_deps):

    accumm_data = {'accumulators': accumulators,
                   'accumulators_deps': accumulators_deps}

    serial = salt.payload.Serial(__opts__)
    with open(_get_accumulator_filepath(), 'w+b') as f:
        serial.dump(accumm_data, f)