    def __init__(self, path):
        assert isdir(path)
        self.path = path
        meta_path = join(path, 'meta.yaml')
        self.meta = parse(open(meta_path).read())