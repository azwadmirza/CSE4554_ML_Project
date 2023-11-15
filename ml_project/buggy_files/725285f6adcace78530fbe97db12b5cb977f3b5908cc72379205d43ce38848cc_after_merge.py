def enforce_state(module, params):
    """
    Add or remove key.
    """

    host = params["name"].lower()
    key = params.get("key", None)
    path = params.get("path")
    hash_host = params.get("hash_host")
    state = params.get("state")
    # Find the ssh-keygen binary
    sshkeygen = module.get_bin_path("ssh-keygen", True)

    if not key and state != "absent":
        module.fail_json(msg="No key specified when adding a host")

    if key and hash_host:
        key = hash_host_key(host, key)

    # Trailing newline in files gets lost, so re-add if necessary
    if key and not key.endswith('\n'):
        key += '\n'

    sanity_check(module, host, key, sshkeygen)

    found, replace_or_add, found_line = search_for_host_key(module, host, key, path, sshkeygen)

    params['diff'] = compute_diff(path, found_line, replace_or_add, state, key)

    # We will change state if found==True & state!="present"
    # or found==False & state=="present"
    # i.e found XOR (state=="present")
    # Alternatively, if replace is true (i.e. key present, and we must change
    # it)
    if module.check_mode:
        module.exit_json(changed=replace_or_add or (state == "present") != found,
                         diff=params['diff'])

    # Now do the work.

    # Only remove whole host if found and no key provided
    if found and not key and state == "absent":
        module.run_command([sshkeygen, '-R', host, '-f', path], check_rc=True)
        params['changed'] = True

    # Next, add a new (or replacing) entry
    if replace_or_add or found != (state == "present"):
        try:
            inf = open(path, "r")
        except IOError as e:
            if e.errno == errno.ENOENT:
                inf = None
            else:
                module.fail_json(msg="Failed to read %s: %s" % (path, str(e)))
        try:
            with tempfile.NamedTemporaryFile(mode='w+', dir=os.path.dirname(path), delete=False) as outf:
                if inf is not None:
                    for line_number, line in enumerate(inf):
                        if found_line == (line_number + 1) and (replace_or_add or state == 'absent'):
                            continue  # skip this line to replace its key
                        outf.write(line)
                    inf.close()
                if state == 'present':
                    outf.write(key)
        except (IOError, OSError) as e:
            module.fail_json(msg="Failed to write to file %s: %s" % (path, to_native(e)))
        else:
            module.atomic_move(outf.name, path)

        params['changed'] = True

    return params