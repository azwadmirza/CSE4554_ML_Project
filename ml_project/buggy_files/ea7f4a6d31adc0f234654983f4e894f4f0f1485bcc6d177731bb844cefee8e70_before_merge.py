def expand_meta_parameters(trans, tool, incoming):
    """
    Take in a dictionary of raw incoming parameters and expand to a list
    of expanded incoming parameters (one set of parameters per tool
    execution).
    """

    to_remove = []
    for key in incoming.keys():
        if key.endswith("|__identifier__"):
            to_remove.append(key)
    for key in to_remove:
        incoming.pop(key)

    # If we're going to multiply input dataset combinations
    # order matters, so the following reorders incoming
    # according to tool.inputs (which is ordered).
    incoming_copy = incoming.copy()
    nested_dict = {}
    for incoming_key in incoming_copy:
        if not incoming_key.startswith('__'):
            process_key(incoming_key, d=nested_dict)

    reordered_incoming = OrderedDict()

    def visitor(input, value, prefix, prefixed_name, prefixed_label, error, **kwargs):
        if prefixed_name in incoming_copy:
            reordered_incoming[prefixed_name] = incoming_copy[prefixed_name]
            del incoming_copy[prefixed_name]

    visit_input_values(inputs=tool.inputs, input_values=nested_dict, callback=visitor)
    reordered_incoming.update(incoming_copy)

    def classifier(input_key):
        value = incoming[input_key]
        if isinstance(value, dict) and 'values' in value:
            # Explicit meta wrapper for inputs...
            is_batch = value.get('batch', False)
            is_linked = value.get('linked', True)
            if is_batch and is_linked:
                classification = permutations.input_classification.MATCHED
            elif is_batch:
                classification = permutations.input_classification.MULTIPLIED
            else:
                classification = permutations.input_classification.SINGLE
            if __collection_multirun_parameter(value):
                collection_value = value['values'][0]
                values = __expand_collection_parameter(trans, input_key, collection_value, collections_to_match, linked=is_linked)
            else:
                values = value['values']
        else:
            classification = permutations.input_classification.SINGLE
            values = value
        return classification, values

    from galaxy.dataset_collections import matching
    collections_to_match = matching.CollectionsToMatch()

    # Stick an unexpanded version of multirun keys so they can be replaced,
    # by expand_mult_inputs.
    incoming_template = reordered_incoming

    expanded_incomings = permutations.expand_multi_inputs(incoming_template, classifier)
    if collections_to_match.has_collections():
        collection_info = trans.app.dataset_collections_service.match_collections(collections_to_match)
    else:
        collection_info = None
    return expanded_incomings, collection_info