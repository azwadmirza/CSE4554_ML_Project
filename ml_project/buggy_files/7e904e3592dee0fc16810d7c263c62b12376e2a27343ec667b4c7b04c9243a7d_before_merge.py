def process_key(incoming_key, d):
    key_parts = incoming_key.split('|')
    if len(key_parts) == 1:
        # Regular parameter
        d[incoming_key] = object()
    elif key_parts[0].rsplit('_', 1)[-1].isdigit():
        # Repeat
        input_name_index = key_parts[0].rsplit('_', 1)
        input_name, index = input_name_index
        if input_name not in d:
            d[input_name] = []
        subdict = {}
        d[input_name].append(subdict)
        process_key("|".join(key_parts[1:]), d=subdict)
    else:
        # Section / Conditional
        input_name = key_parts[0]
        subdict = {}
        d[input_name] = subdict
        process_key("|".join(key_parts[1:]), d=subdict)