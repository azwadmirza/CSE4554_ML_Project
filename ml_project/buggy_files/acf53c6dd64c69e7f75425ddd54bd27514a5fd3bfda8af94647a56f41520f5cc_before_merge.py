def _extract_tar_file(tar, filename, b_dest, b_temp_path, expected_hash=None):
    n_filename = to_native(filename, errors='surrogate_or_strict')
    try:
        member = tar.getmember(n_filename)
    except KeyError:
        raise AnsibleError("Collection tar at '%s' does not contain the expected file '%s'." % (to_native(tar.name),
                                                                                                n_filename))

    with tempfile.NamedTemporaryFile(dir=b_temp_path, delete=False) as tmpfile_obj:
        bufsize = 65536
        sha256_digest = sha256()
        with _tarfile_extract(tar, member) as tar_obj:
            data = tar_obj.read(bufsize)
            while data:
                tmpfile_obj.write(data)
                tmpfile_obj.flush()
                sha256_digest.update(data)
                data = tar_obj.read(bufsize)

        actual_hash = sha256_digest.hexdigest()

        if expected_hash and actual_hash != expected_hash:
            raise AnsibleError("Checksum mismatch for '%s' inside collection at '%s'"
                               % (n_filename, to_native(tar.name)))

        b_dest_filepath = os.path.abspath(os.path.join(b_dest, to_bytes(filename, errors='surrogate_or_strict')))
        b_parent_dir = os.path.dirname(b_dest_filepath)
        if b_parent_dir != b_dest and not b_parent_dir.startswith(b_dest + to_bytes(os.path.sep)):
            raise AnsibleError("Cannot extract tar entry '%s' as it will be placed outside the collection directory"
                               % to_native(filename, errors='surrogate_or_strict'))

        if not os.path.exists(b_parent_dir):
            # Seems like Galaxy does not validate if all file entries have a corresponding dir ftype entry. This check
            # makes sure we create the parent directory even if it wasn't set in the metadata.
            os.makedirs(b_parent_dir, mode=0o0755)

        shutil.move(to_bytes(tmpfile_obj.name, errors='surrogate_or_strict'), b_dest_filepath)

        # Default to rw-r--r-- and only add execute if the tar file has execute.
        new_mode = 0o644
        if stat.S_IMODE(member.mode) & stat.S_IXUSR:
            new_mode |= 0o0111

        os.chmod(b_dest_filepath, new_mode)