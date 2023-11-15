def main():
    argument_spec = url_argument_spec()
    argument_spec.update(
        url=dict(type='str', required=True),
        dest=dict(type='path', required=True),
        backup=dict(type='bool'),
        sha256sum=dict(type='str', default=''),
        checksum=dict(type='str', default=''),
        timeout=dict(type='int', default=10),
        headers=dict(type='raw'),
        tmp_dest=dict(type='path'),
    )

    module = AnsibleModule(
        # not checking because of daisy chain to file module
        argument_spec=argument_spec,
        add_file_common_args=True,
        supports_check_mode=True,
        mutually_exclusive=[['checksum', 'sha256sum']],
    )

    url = module.params['url']
    dest = module.params['dest']
    backup = module.params['backup']
    force = module.params['force']
    sha256sum = module.params['sha256sum']
    checksum = module.params['checksum']
    use_proxy = module.params['use_proxy']
    timeout = module.params['timeout']
    tmp_dest = module.params['tmp_dest']

    # Parse headers to dict
    if isinstance(module.params['headers'], dict):
        headers = module.params['headers']
    elif module.params['headers']:
        try:
            headers = dict(item.split(':', 1) for item in module.params['headers'].split(','))
            module.deprecate('Supplying `headers` as a string is deprecated. Please use dict/hash format for `headers`', version='2.10')
        except Exception:
            module.fail_json(msg="The string representation for the `headers` parameter requires a key:value,key:value syntax to be properly parsed.")
    else:
        headers = None

    dest_is_dir = os.path.isdir(dest)
    last_mod_time = None

    # workaround for usage of deprecated sha256sum parameter
    if sha256sum:
        checksum = 'sha256:%s' % (sha256sum)

    # checksum specified, parse for algorithm and checksum
    if checksum:
        try:
            algorithm, checksum = checksum.split(':', 1)
            if checksum.startswith('http://') or checksum.startswith('https://') or checksum.startswith('ftp://'):
                checksum_url = checksum
                # download checksum file to checksum_tmpsrc
                checksum_tmpsrc, checksum_info = url_get(module, checksum_url, dest, use_proxy, last_mod_time, force, timeout, headers, tmp_dest)
                with open(checksum_tmpsrc) as f:
                    lines = [line.rstrip('\n') for line in f]
                os.remove(checksum_tmpsrc)
                lines = dict(s.split(None, 1) for s in lines)
                filename = url_filename(url)

                # Look through each line in the checksum file for a hash corresponding to
                # the filename in the url, returning the first hash that is found.
                for cksum in (s for (s, f) in lines.items() if f.strip('./') == filename):
                    checksum = cksum
                    break
                else:
                    checksum = None

                if checksum is None:
                    module.fail_json("Unable to find a checksum for file '%s' in '%s'" % (filename, checksum_url))
            # Remove any non-alphanumeric characters, including the infamous
            # Unicode zero-width space
            checksum = re.sub(r'\W+', '', checksum).lower()
            # Ensure the checksum portion is a hexdigest
            int(checksum, 16)
        except ValueError:
            module.fail_json(msg="The checksum parameter has to be in format <algorithm>:<checksum>")

    if not dest_is_dir and os.path.exists(dest):
        checksum_mismatch = False

        # If the download is not forced and there is a checksum, allow
        # checksum match to skip the download.
        if not force and checksum != '':
            destination_checksum = module.digest_from_file(dest, algorithm)

            if checksum != destination_checksum:
                checksum_mismatch = True

        # Not forcing redownload, unless checksum does not match
        if not force and not checksum_mismatch:
            # Not forcing redownload, unless checksum does not match
            # allow file attribute changes
            module.params['path'] = dest
            file_args = module.load_file_common_arguments(module.params)
            file_args['path'] = dest
            changed = module.set_fs_attributes_if_different(file_args, False)
            if changed:
                module.exit_json(msg="file already exists but file attributes changed", dest=dest, url=url, changed=changed)
            module.exit_json(msg="file already exists", dest=dest, url=url, changed=changed)

        # If the file already exists, prepare the last modified time for the
        # request.
        mtime = os.path.getmtime(dest)
        last_mod_time = datetime.datetime.utcfromtimestamp(mtime)

        # If the checksum does not match we have to force the download
        # because last_mod_time may be newer than on remote
        if checksum_mismatch:
            force = True

    # download to tmpsrc
    tmpsrc, info = url_get(module, url, dest, use_proxy, last_mod_time, force, timeout, headers, tmp_dest)

    # Now the request has completed, we can finally generate the final
    # destination file name from the info dict.

    if dest_is_dir:
        filename = extract_filename_from_headers(info)
        if not filename:
            # Fall back to extracting the filename from the URL.
            # Pluck the URL from the info, since a redirect could have changed
            # it.
            filename = url_filename(info['url'])
        dest = os.path.join(dest, filename)

    checksum_src = None
    checksum_dest = None

    # raise an error if there is no tmpsrc file
    if not os.path.exists(tmpsrc):
        os.remove(tmpsrc)
        module.fail_json(msg="Request failed", status_code=info['status'], response=info['msg'])
    if not os.access(tmpsrc, os.R_OK):
        os.remove(tmpsrc)
        module.fail_json(msg="Source %s is not readable" % (tmpsrc))
    checksum_src = module.sha1(tmpsrc)

    # check if there is no dest file
    if os.path.exists(dest):
        # raise an error if copy has no permission on dest
        if not os.access(dest, os.W_OK):
            os.remove(tmpsrc)
            module.fail_json(msg="Destination %s is not writable" % (dest))
        if not os.access(dest, os.R_OK):
            os.remove(tmpsrc)
            module.fail_json(msg="Destination %s is not readable" % (dest))
        checksum_dest = module.sha1(dest)
    else:
        if not os.path.exists(os.path.dirname(dest)):
            os.remove(tmpsrc)
            module.fail_json(msg="Destination %s does not exist" % (os.path.dirname(dest)))
        if not os.access(os.path.dirname(dest), os.W_OK):
            os.remove(tmpsrc)
            module.fail_json(msg="Destination %s is not writable" % (os.path.dirname(dest)))

    if module.check_mode:
        if os.path.exists(tmpsrc):
            os.remove(tmpsrc)
        changed = (checksum_dest is None or
                   checksum_src != checksum_dest)
        res_args = dict(url=url, changed=changed, dest=dest, src=tmpsrc,
                        checksum_dest=checksum_dest, checksum_src=checksum_src,
                        msg=info.get('msg', ''))
        module.exit_json(**res_args)

    backup_file = None
    if checksum_src != checksum_dest:
        try:
            if backup:
                if os.path.exists(dest):
                    backup_file = module.backup_local(dest)
            module.atomic_move(tmpsrc, dest)
        except Exception as e:
            if os.path.exists(tmpsrc):
                os.remove(tmpsrc)
            module.fail_json(msg="failed to copy %s to %s: %s" % (tmpsrc, dest, to_native(e)),
                             exception=traceback.format_exc())
        changed = True
    else:
        changed = False
        if os.path.exists(tmpsrc):
            os.remove(tmpsrc)

    if checksum != '':
        destination_checksum = module.digest_from_file(dest, algorithm)

        if checksum != destination_checksum:
            os.remove(dest)
            module.fail_json(msg="The checksum for %s did not match %s; it was %s." % (dest, checksum, destination_checksum))

    # allow file attribute changes
    module.params['path'] = dest
    file_args = module.load_file_common_arguments(module.params)
    file_args['path'] = dest
    changed = module.set_fs_attributes_if_different(file_args, changed)

    # Backwards compat only.  We'll return None on FIPS enabled systems
    try:
        md5sum = module.md5(dest)
    except ValueError:
        md5sum = None

    res_args = dict(
        url=url, dest=dest, src=tmpsrc, md5sum=md5sum, checksum_src=checksum_src,
        checksum_dest=checksum_dest, changed=changed, msg=info.get('msg', ''), status_code=info.get('status', '')
    )
    if backup_file:
        res_args['backup_file'] = backup_file

    # Mission complete
    module.exit_json(**res_args)