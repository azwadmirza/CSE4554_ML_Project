def sanity_check(module, host, key, sshkeygen):
    '''Check supplied key is sensible

    host and key are parameters provided by the user; If the host
    provided is inconsistent with the key supplied, then this function
    quits, providing an error to the user.
    sshkeygen is the path to ssh-keygen, found earlier with get_bin_path
    '''
    # If no key supplied, we're doing a removal, and have nothing to check here.
    if key is None:
        return
    # Rather than parsing the key ourselves, get ssh-keygen to do it
    # (this is essential for hashed keys, but otherwise useful, as the
    # key question is whether ssh-keygen thinks the key matches the host).

    # The approach is to write the key to a temporary file,
    # and then attempt to look up the specified host in that file.

    if re.search(r'\S+(\s+)?,(\s+)?', host):
        module.fail_json(msg="Comma separated list of names is not supported. "
                             "Please pass a single name to lookup in the known_hosts file.")

    try:
        outf = tempfile.NamedTemporaryFile(mode='w+')
        outf.write(key)
        outf.flush()
    except IOError as e:
        module.fail_json(msg="Failed to write to temporary file %s: %s" %
                             (outf.name, to_native(e)))

    sshkeygen_command = [sshkeygen, '-F', host, '-f', outf.name]
    rc, stdout, stderr = module.run_command(sshkeygen_command)
    try:
        outf.close()
    except:
        pass

    if stdout == '':  # host not found
        module.fail_json(msg="Host parameter does not match hashed host field in supplied key")