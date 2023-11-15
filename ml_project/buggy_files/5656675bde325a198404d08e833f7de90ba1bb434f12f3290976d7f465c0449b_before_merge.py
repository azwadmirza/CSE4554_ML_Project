def unpack_source_tree(tree_file, dir=None):
    if dir is None:
        dir = tempfile.mkdtemp()
    header = []
    cur_file = None
    f = open(tree_file)
    try:
        lines = f.readlines()
    finally:
        f.close()
    del f
    try:
        for line in lines:
            if line[:5] == '#####':
                filename = line.strip().strip('#').strip().replace('/', os.path.sep)
                path = os.path.join(dir, filename)
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                if cur_file is not None:
                    f, cur_file = cur_file, None
                    f.close()
                cur_file = open(path, 'w')
            elif cur_file is not None:
                cur_file.write(line)
            elif line.strip() and not line.lstrip().startswith('#'):
                if line.strip() not in ('"""', "'''"):
                    header.append(line)
    finally:
        if cur_file is not None:
            cur_file.close()
    return dir, ''.join(header)