def __cleanup_param_values(inputs, values):
    """
    Remove 'Data' values from `param_values`, along with metadata cruft,
    but track the associations.
    """
    associations = []
    # dbkey is pushed in by the framework
    if 'dbkey' in values:
        del values['dbkey']
    root_values = values
    root_input_keys = inputs.keys()

    # Recursively clean data inputs and dynamic selects
    def cleanup(prefix, inputs, values):
        for key, input in inputs.items():
            if isinstance(input, DataToolParameter) or isinstance(input, DataCollectionToolParameter):
                tmp = values[key]
                values[key] = None
                # HACK: Nested associations are not yet working, but we
                #       still need to clean them up so we can serialize
                # if not( prefix ):
                if isinstance(tmp, model.DatasetCollectionElement):
                    tmp = tmp.first_dataset_instance()
                if tmp:  # this is false for a non-set optional dataset
                    if not isinstance(tmp, list):
                        associations.append((tmp.hid, prefix + key))
                    else:
                        associations.extend([(t.hid, prefix + key) for t in tmp])

                # Cleanup the other deprecated crap associated with datasets
                # as well. Worse, for nested datasets all the metadata is
                # being pushed into the root. FIXME: MUST REMOVE SOON
                key = prefix + key + "_"
                for k in root_values.keys():
                    if k not in root_input_keys and k.startswith(key):
                        del root_values[k]
            elif isinstance(input, Repeat):
                if key in values:
                    group_values = values[key]
                    for i, rep_values in enumerate(group_values):
                        rep_index = rep_values['__index__']
                        cleanup("%s%s_%d|" % (prefix, key, rep_index), input.inputs, group_values[i])
            elif isinstance(input, Conditional):
                # Scrub dynamic resource related parameters from workflows,
                # they cause problems and the workflow probably should include
                # their state in workflow encoding.
                if input.name == '__job_resource':
                    if input.name in values:
                        del values[input.name]
                    return
                if input.name in values:
                    group_values = values[input.name]
                    current_case = group_values['__current_case__']
                    cleanup("%s%s|" % (prefix, key), input.cases[current_case].inputs, group_values)
            elif isinstance(input, Section):
                if input.name in values:
                    cleanup("%s%s|" % (prefix, key), input.inputs, values[input.name])
    cleanup("", inputs, values)
    return associations