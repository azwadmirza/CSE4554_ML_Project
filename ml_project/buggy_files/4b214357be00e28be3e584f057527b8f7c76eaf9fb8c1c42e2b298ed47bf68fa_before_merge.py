def glob_files_remotely(cmd, client, share_name, pattern):
    """glob the files in remote file share based on the given pattern"""
    from collections import deque
    t_dir, t_file = cmd.get_models('file.models#Directory', 'file.models#File')

    queue = deque([""])
    while queue:
        current_dir = queue.pop()
        for f in client.list_directories_and_files(share_name, current_dir):
            if isinstance(f, t_file):
                if not pattern or _match_path(os.path.join(current_dir, f.name), pattern):
                    yield current_dir, f.name
            elif isinstance(f, t_dir):
                queue.appendleft(os.path.join(current_dir, f.name))