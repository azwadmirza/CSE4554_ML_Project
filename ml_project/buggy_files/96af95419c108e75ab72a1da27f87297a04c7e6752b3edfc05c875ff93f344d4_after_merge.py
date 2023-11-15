    def __init__(self, f: IO):
        self.mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)