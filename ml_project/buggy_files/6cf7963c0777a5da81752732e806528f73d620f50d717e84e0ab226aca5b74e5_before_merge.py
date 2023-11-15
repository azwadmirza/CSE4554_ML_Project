def get_egg_info_files(sp_dir):
    for fn in os.listdir(sp_dir):
        if fn.endswith('.egg-link'):
            with open(join(sp_dir, fn), 'r') as reader:
                for egg in get_egg_info_files(reader.readline().strip()):
                    yield egg
        if not fn.endswith(('.egg', '.egg-info', '.dist-info')):
            continue
        path = join(sp_dir, fn)
        if isfile(path):
            yield path
        elif isdir(path):
            for path2 in [join(path, 'PKG-INFO'),
                          join(path, 'EGG-INFO', 'PKG-INFO'),
                          join(path, 'METADATA')]:
                if isfile(path2):
                    yield path2