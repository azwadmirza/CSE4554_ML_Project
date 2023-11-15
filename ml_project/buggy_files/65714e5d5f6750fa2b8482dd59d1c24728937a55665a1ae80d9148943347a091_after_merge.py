def recursive_set_attributes(module, b_path, follow, file_args):
    changed = False
    for b_root, b_dirs, b_files in os.walk(b_path):
        for b_fsobj in b_dirs + b_files:
            b_fsname = os.path.join(b_root, b_fsobj)
            if not os.path.islink(b_fsname):
                tmp_file_args = file_args.copy()
                tmp_file_args['path'] = to_native(b_fsname, errors='surrogate_or_strict')
                changed |= module.set_fs_attributes_if_different(tmp_file_args, changed, expand=False)
            else:
                # Change perms on the link
                tmp_file_args = file_args.copy()
                tmp_file_args['path'] = to_native(b_fsname, errors='surrogate_or_strict')
                changed |= module.set_fs_attributes_if_different(tmp_file_args, changed, expand=False)

                if follow:
                    b_fsname = os.path.join(b_root, os.readlink(b_fsname))
                    # The link target could be nonexistent
                    if os.path.exists(b_fsname):
                        if os.path.isdir(b_fsname):
                            # Link is a directory so change perms on the directory's contents
                            changed |= recursive_set_attributes(module, b_fsname, follow, file_args)

                        # Change perms on the file pointed to by the link
                        tmp_file_args = file_args.copy()
                        tmp_file_args['path'] = to_native(b_fsname, errors='surrogate_or_strict')
                        changed |= module.set_fs_attributes_if_different(tmp_file_args, changed, expand=False)
    return changed