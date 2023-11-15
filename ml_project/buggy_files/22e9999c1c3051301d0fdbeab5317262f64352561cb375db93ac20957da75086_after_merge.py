def _extract_tar_dir(tar, dirname, b_dest):
    """ Extracts a directory from a collection tar. """
    member_names = [to_native(dirname, errors='surrogate_or_strict')]

    # Create list of members with and without trailing separator
    if not member_names[-1].endswith(os.path.sep):
        member_names.append(member_names[-1] + os.path.sep)

    # Try all of the member names and stop on the first one that are able to successfully get
    for member in member_names:
        try:
            tar_member = tar.getmember(member)
        except KeyError:
            continue
        break
    else:
        # If we still can't find the member, raise a nice error.
        raise AnsibleError("Unable to extract '%s' from collection" % to_native(member, errors='surrogate_or_strict'))

    b_dir_path = os.path.join(b_dest, to_bytes(dirname, errors='surrogate_or_strict'))

    b_parent_path = os.path.dirname(b_dir_path)
    try:
        os.makedirs(b_parent_path, mode=0o0755)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if tar_member.type == tarfile.SYMTYPE:
        b_link_path = to_bytes(tar_member.linkname, errors='surrogate_or_strict')
        if not _is_child_path(b_link_path, b_dest, link_name=b_dir_path):
            raise AnsibleError("Cannot extract symlink '%s' in collection: path points to location outside of "
                               "collection '%s'" % (to_native(dirname), b_link_path))

        os.symlink(b_link_path, b_dir_path)

    else:
        if not os.path.isdir(b_dir_path):
            os.mkdir(b_dir_path, 0o0755)