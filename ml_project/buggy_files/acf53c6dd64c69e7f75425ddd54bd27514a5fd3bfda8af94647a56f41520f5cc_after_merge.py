def _extract_tar_file(tar, filename, b_dest, b_temp_path, expected_hash=None):
    """ Extracts a file from a collection tar. """
    n_filename = to_native(filename, errors='surrogate_or_strict')
    with _get_tar_file_member(tar, filename) as (tar_member, tar_obj):
        if tar_member.type == tarfile.SYMTYPE:
            actual_hash = _consume_file(tar_obj)

        else:
            with tempfile.NamedTemporaryFile(dir=b_temp_path, delete=False) as tmpfile_obj:
                actual_hash = _consume_file(tar_obj, tmpfile_obj)

        if expected_hash and actual_hash != expected_hash:
            raise AnsibleError("Checksum mismatch for '%s' inside collection at '%s'"
                               % (n_filename, to_native(tar.name)))

        b_dest_filepath = os.path.abspath(os.path.join(b_dest, to_bytes(filename, errors='surrogate_or_strict')))
        b_parent_dir = os.path.dirname(b_dest_filepath)
        if not _is_child_path(b_parent_dir, b_dest):
            raise AnsibleError("Cannot extract tar entry '%s' as it will be placed outside the collection directory"
                               % to_native(filename, errors='surrogate_or_strict'))

        if not os.path.exists(b_parent_dir):
            # Seems like Galaxy does not validate if all file entries have a corresponding dir ftype entry. This check
            # makes sure we create the parent directory even if it wasn't set in the metadata.
            os.makedirs(b_parent_dir, mode=0o0755)

        if tar_member.type == tarfile.SYMTYPE:
            b_link_path = to_bytes(tar_member.linkname, errors='surrogate_or_strict')
            if not _is_child_path(b_link_path, b_dest, link_name=b_dest_filepath):
                raise AnsibleError("Cannot extract symlink '%s' in collection: path points to location outside of "
                                   "collection '%s'" % (to_native(filename), b_link_path))

            os.symlink(b_link_path, b_dest_filepath)

        else:
            shutil.move(to_bytes(tmpfile_obj.name, errors='surrogate_or_strict'), b_dest_filepath)

            # Default to rw-r--r-- and only add execute if the tar file has execute.
            tar_member = tar.getmember(to_native(filename, errors='surrogate_or_strict'))
            new_mode = 0o644
            if stat.S_IMODE(tar_member.mode) & stat.S_IXUSR:
                new_mode |= 0o0111

            os.chmod(b_dest_filepath, new_mode)