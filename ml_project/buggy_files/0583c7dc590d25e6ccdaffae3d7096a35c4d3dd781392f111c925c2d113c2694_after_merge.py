    def __init__(self, path):
        self.path = path
        self.end = "-" + str(os.getpid())
        self.lock_path = join(self.path, LOCKFN + self.end)
        self.pattern = join(self.path, LOCKFN + '-*')
        self.remove = True