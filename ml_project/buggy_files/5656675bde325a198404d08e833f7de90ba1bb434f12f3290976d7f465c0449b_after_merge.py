def unpack_source_tree(tree_file, workdir, cython_root):
    programs = {
        'PYTHON': [sys.executable],
        'CYTHON': [sys.executable, os.path.join(cython_root, 'cython.py')],
        'CYTHONIZE': [sys.executable, os.path.join(cython_root, 'cythonize.py')]
    }

    if workdir is None:
        workdir = tempfile.mkdtemp()
    header, cur_file = [], None
    with open(tree_file) as f:
        try:
            for line in f:
                if line.startswith('#####'):
                    filename = line.strip().strip('#').strip().replace('/', os.path.sep)
                    path = os.path.join(workdir, filename)
                    if not os.path.exists(os.path.dirname(path)):
                        os.makedirs(os.path.dirname(path))
                    if cur_file is not None:
                        to_close, cur_file = cur_file, None
                        to_close.close()
                    cur_file = open(path, 'w')
                elif cur_file is not None:
                    cur_file.write(line)
                elif line.strip() and not line.lstrip().startswith('#'):
                    if line.strip() not in ('"""', "'''"):
                        command = shlex.split(line)
                        if not command: continue
                        # In Python 3: prog, *args = command
                        prog, args = command[0], command[1:]
                        try:
                            header.append(programs[prog]+args)
                        except KeyError:
                            header.append(command)
        finally:
            if cur_file is not None:
                cur_file.close()
    return workdir, header