def search_for_host_key(module, host, key, hash_host, path, sshkeygen):
    '''search_for_host_key(module,host,key,path,sshkeygen) -> (found,replace_or_add,found_line)

    Looks up host and keytype in the known_hosts file path; if it's there, looks to see
    if one of those entries matches key. Returns:
    found (Boolean): is host found in path?
    replace_or_add (Boolean): is the key in path different to that supplied by user?
    found_line (int or None): the line where a key of the same type was found
    if found=False, then replace is always False.
    sshkeygen is the path to ssh-keygen, found earlier with get_bin_path
    '''
    if os.path.exists(path) is False:
        return False, False, None, key

    sshkeygen_command = [sshkeygen, '-F', host, '-f', path]

    # openssh >=6.4 has changed ssh-keygen behaviour such that it returns
    # 1 if no host is found, whereas previously it returned 0
    rc, stdout, stderr = module.run_command(sshkeygen_command, check_rc=False)
    if stdout == '' and stderr == '' and (rc == 0 or rc == 1):
        return False, False, None, key  # host not found, no other errors
    if rc != 0:  # something went wrong
        module.fail_json(msg="ssh-keygen failed (rc=%d, stdout='%s',stderr='%s')" % (rc, stdout, stderr))

    # If user supplied no key, we don't want to try and replace anything with it
    if key is None:
        return True, False, None, key

    lines = stdout.split('\n')
    new_key = normalize_known_hosts_key(key)

    sshkeygen_command.insert(1, '-H')
    rc, stdout, stderr = module.run_command(sshkeygen_command, check_rc=False)
    if rc not in (0, 1) or stderr != '':  # something went wrong
        module.fail_json(msg="ssh-keygen failed to hash host (rc=%d, stdout='%s',stderr='%s')" % (rc, stdout, stderr))
    hashed_lines = stdout.split('\n')

    for lnum, l in enumerate(lines):
        if l == '':
            continue
        elif l[0] == '#':  # info output from ssh-keygen; contains the line number where key was found
            try:
                # This output format has been hardcoded in ssh-keygen since at least OpenSSH 4.0
                # It always outputs the non-localized comment before the found key
                found_line = int(re.search(r'found: line (\d+)', l).group(1))
            except IndexError:
                module.fail_json(msg="failed to parse output of ssh-keygen for line number: '%s'" % l)
        else:
            found_key = normalize_known_hosts_key(l)
            if hash_host is True:
                if found_key['host'][:3] == '|1|':
                    new_key['host'] = found_key['host']
                else:
                    hashed_host = normalize_known_hosts_key(hashed_lines[lnum])
                    found_key['host'] = hashed_host['host']
                key = key.replace(host, found_key['host'])
            if new_key == found_key:  # found a match
                return True, False, found_line, key  # found exactly the same key, don't replace
            elif new_key['type'] == found_key['type']:  # found a different key for the same key type
                return True, True, found_line, key
    # No match found, return found and replace, but no line
    return True, True, None, key