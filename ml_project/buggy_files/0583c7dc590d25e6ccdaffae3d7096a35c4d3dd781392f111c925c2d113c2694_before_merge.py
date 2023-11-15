    def __init__(self, path, retries=10):
        self.path = path
        self.end = "-" + str(os.getpid())
        self.lock_path = os.path.join(self.path, LOCKFN + self.end)
        self.retries = retries