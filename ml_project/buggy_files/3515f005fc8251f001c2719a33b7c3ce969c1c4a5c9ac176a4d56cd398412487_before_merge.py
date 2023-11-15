def _construct_pillar(top_dir, follow_dir_links, keep_newline=False):
    '''
    Construct pillar from file tree.
    '''
    pillar = {}

    norm_top_dir = os.path.normpath(top_dir)
    for dir_path, dir_names, file_names in os.walk(
            top_dir, topdown=True, onerror=_on_walk_error,
            followlinks=follow_dir_links):
        # Find current path in pillar tree
        pillar_node = pillar
        norm_dir_path = os.path.normpath(dir_path)
        if norm_dir_path != norm_top_dir:
            prefix = rel_path = os.path.relpath(norm_dir_path, norm_top_dir)
            path_parts = []
            while rel_path:
                rel_path, tail = os.path.split(rel_path)
                path_parts.insert(0, tail)
            while path_parts:
                pillar_node = pillar_node[path_parts.pop(0)]

        # Create dicts for subdirectories
        for dir_name in dir_names:
            pillar_node[dir_name] = {}

        # Add files
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            if not os.path.isfile(file_path):
                log.error('file_tree: %s: not a regular file', file_path)
                continue

            contents = ''
            try:
                with salt.utils.fopen(file_path, 'rb') as fhr:
                    buf = fhr.read(__opts__['file_buffer_size'])
                    while buf:
                        contents += buf
                        buf = fhr.read(__opts__['file_buffer_size'])
                    if contents.endswith('\n') \
                            and _check_newline(prefix,
                                               file_name,
                                               keep_newline):
                        contents = contents[:-1]
            except (IOError, OSError) as exc:
                log.error('file_tree: Error reading %s: %s',
                          file_path,
                          exc.strerror)
            else:
                pillar_node[file_name] = contents

    return pillar