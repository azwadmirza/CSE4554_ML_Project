def enforce_state(module, params):
    """
    Add or remove key.
    """

    user        = params["user"]
    key         = params["key"]
    path        = params.get("path", None)
    manage_dir  = params.get("manage_dir", True)
    state       = params.get("state", "present")
    key_options = params.get("key_options", None)
    exclusive   = params.get("exclusive", False)
    error_msg   = "Error getting key from: %s"

    # if the key is a url, request it and use it as key source
    if key.startswith("http"):
        try:
            resp, info = fetch_url(module, key)
            if info['status'] != 200:
                module.fail_json(msg=error_msg % key)
            else:
                key = resp.read()
        except Exception:
            module.fail_json(msg=error_msg % key)

    # extract individual keys into an array, skipping blank lines and comments
    new_keys = [s for s in key.splitlines() if s and not s.startswith('#')]

    # check current state -- just get the filename, don't create file
    do_write = False
    params["keyfile"] = keyfile(module, user, do_write, path, manage_dir)
    existing_content = readfile(params["keyfile"])
    existing_keys = parsekeys(module, existing_content)

    # Add a place holder for keys that should exist in the state=present and
    # exclusive=true case
    keys_to_exist = []

    # we will order any non exclusive new keys higher than all the existing keys,
    # resulting in the new keys being written to the key file after existing keys, but
    # in the order of new_keys
    max_rank_of_existing_keys = len(existing_keys)

    # Check our new keys, if any of them exist we'll continue.
    for rank_index, new_key in enumerate(new_keys):
        parsed_new_key = parsekey(module, new_key, rank=rank_index)

        if not parsed_new_key:
            module.fail_json(msg="invalid key specified: %s" % new_key)

        if key_options is not None:
            parsed_options = parseoptions(module, key_options)
            # rank here is the rank in the provided new keys, which may be unrelated to rank in existing_keys
            parsed_new_key = (parsed_new_key[0], parsed_new_key[1], parsed_options, parsed_new_key[3], parsed_new_key[4])

        matched = False
        non_matching_keys = []

        if parsed_new_key[0] in existing_keys:
            # Then we check if everything (except the rank at index 4) matches, including
            # the key type and options. If not, we append this
            # existing key to the non-matching list
            # We only want it to match everything when the state
            # is present
            if parsed_new_key[:4] != existing_keys[parsed_new_key[0]][:4] and state == "present":
                non_matching_keys.append(existing_keys[parsed_new_key[0]])
            else:
                matched = True

        # handle idempotent state=present
        if state=="present":
            keys_to_exist.append(parsed_new_key[0])
            if len(non_matching_keys) > 0:
                for non_matching_key in non_matching_keys:
                    if non_matching_key[0] in existing_keys:
                        del existing_keys[non_matching_key[0]]
                        do_write = True

            # new key that didn't exist before. Where should it go in the ordering?
            if not matched:
                # We want the new key to be after existing keys if not exclusive (rank > max_rank_of_existing_keys)
                total_rank = max_rank_of_existing_keys + parsed_new_key[4]
                # replace existing key tuple with new parsed key with its total rank
                existing_keys[parsed_new_key[0]] = (parsed_new_key[0], parsed_new_key[1], parsed_new_key[2], parsed_new_key[3], total_rank)
                do_write = True

        elif state=="absent":
            if not matched:
                continue
            del existing_keys[parsed_new_key[0]]
            do_write = True

    # remove all other keys to honor exclusive
    # for 'exclusive', make sure keys are written in the order the new keys were
    if state == "present" and exclusive:
        to_remove = frozenset(existing_keys).difference(keys_to_exist)
        for key in to_remove:
            del existing_keys[key]
            do_write = True

    if do_write:
        filename = keyfile(module, user, do_write, path, manage_dir)
        new_content = serialize(existing_keys)
        diff = {
            'before_header': params['keyfile'],
            'after_header': filename,
            'before': existing_content,
            'after': new_content,
        }
        if module.check_mode:
            module.exit_json(changed=True, diff=diff)
        writefile(module, filename, new_content)
        params['changed'] = True
        params['diff'] = diff
    else:
        if module.check_mode:
            module.exit_json(changed=False)

    return params