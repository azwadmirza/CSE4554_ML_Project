def __virtual__():
    """
    Only works on Windows systems
    """
    if salt.utils.platform.is_windows():
        if HAS_WINDOWS_MODULES:
            # Load functions from file.py
            global get_managed, manage_file
            global source_list, __clean_tmp, file_exists
            global check_managed, check_managed_changes, check_file_meta
            global append, _error, directory_exists, touch, contains
            global contains_regex, contains_glob, get_source_sum
            global find, psed, get_sum, check_hash, get_hash, delete_backup
            global get_diff, line, _get_flags, extract_hash, comment_line
            global access, copy, readdir, read, rmdir, truncate, replace, search
            global _binary_replace, _get_bkroot, list_backups, restore_backup
            global _splitlines_preserving_trailing_newline
            global blockreplace, prepend, seek_read, seek_write, rename, lstat
            global write, pardir, join, _add_flags, apply_template_on_contents
            global path_exists_glob, comment, uncomment, _mkstemp_copy
            global _regex_to_static, _set_line_indent, dirname, basename
            global list_backups_dir, normpath_, _assert_occurrence
            global _set_line_eol, _get_eol
            global _set_line

            replace = _namespaced_function(replace, globals())
            search = _namespaced_function(search, globals())
            _get_flags = _namespaced_function(_get_flags, globals())
            _binary_replace = _namespaced_function(_binary_replace, globals())
            _splitlines_preserving_trailing_newline = _namespaced_function(
                _splitlines_preserving_trailing_newline, globals()
            )
            _error = _namespaced_function(_error, globals())
            _get_bkroot = _namespaced_function(_get_bkroot, globals())
            list_backups = _namespaced_function(list_backups, globals())
            restore_backup = _namespaced_function(restore_backup, globals())
            delete_backup = _namespaced_function(delete_backup, globals())
            extract_hash = _namespaced_function(extract_hash, globals())
            append = _namespaced_function(append, globals())
            get_managed = _namespaced_function(get_managed, globals())
            check_managed = _namespaced_function(check_managed, globals())
            check_managed_changes = _namespaced_function(
                check_managed_changes, globals()
            )
            check_file_meta = _namespaced_function(check_file_meta, globals())
            manage_file = _namespaced_function(manage_file, globals())
            source_list = _namespaced_function(source_list, globals())
            file_exists = _namespaced_function(file_exists, globals())
            __clean_tmp = _namespaced_function(__clean_tmp, globals())
            directory_exists = _namespaced_function(directory_exists, globals())
            touch = _namespaced_function(touch, globals())
            contains = _namespaced_function(contains, globals())
            contains_regex = _namespaced_function(contains_regex, globals())
            contains_glob = _namespaced_function(contains_glob, globals())
            get_source_sum = _namespaced_function(get_source_sum, globals())
            find = _namespaced_function(find, globals())
            psed = _namespaced_function(psed, globals())
            get_sum = _namespaced_function(get_sum, globals())
            check_hash = _namespaced_function(check_hash, globals())
            get_hash = _namespaced_function(get_hash, globals())
            get_diff = _namespaced_function(get_diff, globals())
            line = _namespaced_function(line, globals())
            access = _namespaced_function(access, globals())
            copy = _namespaced_function(copy, globals())
            readdir = _namespaced_function(readdir, globals())
            read = _namespaced_function(read, globals())
            rmdir = _namespaced_function(rmdir, globals())
            truncate = _namespaced_function(truncate, globals())
            blockreplace = _namespaced_function(blockreplace, globals())
            prepend = _namespaced_function(prepend, globals())
            seek_read = _namespaced_function(seek_read, globals())
            seek_write = _namespaced_function(seek_write, globals())
            rename = _namespaced_function(rename, globals())
            lstat = _namespaced_function(lstat, globals())
            path_exists_glob = _namespaced_function(path_exists_glob, globals())
            write = _namespaced_function(write, globals())
            pardir = _namespaced_function(pardir, globals())
            join = _namespaced_function(join, globals())
            comment = _namespaced_function(comment, globals())
            uncomment = _namespaced_function(uncomment, globals())
            comment_line = _namespaced_function(comment_line, globals())
            _regex_to_static = _namespaced_function(_regex_to_static, globals())
            _set_line = _namespaced_function(_set_line, globals())
            _set_line_indent = _namespaced_function(_set_line_indent, globals())
            _set_line_eol = _namespaced_function(_set_line_eol, globals())
            _get_eol = _namespaced_function(_get_eol, globals())
            _mkstemp_copy = _namespaced_function(_mkstemp_copy, globals())
            _add_flags = _namespaced_function(_add_flags, globals())
            apply_template_on_contents = _namespaced_function(
                apply_template_on_contents, globals()
            )
            dirname = _namespaced_function(dirname, globals())
            basename = _namespaced_function(basename, globals())
            list_backups_dir = _namespaced_function(list_backups_dir, globals())
            normpath_ = _namespaced_function(normpath_, globals())
            _assert_occurrence = _namespaced_function(_assert_occurrence, globals())

        else:
            return False, "Module win_file: Missing Win32 modules"

    if "dacl.get_owner" not in __utils__:
        return (False, "Module win_file: Unable to load salt.utils.win_dacl")

    return __virtualname__