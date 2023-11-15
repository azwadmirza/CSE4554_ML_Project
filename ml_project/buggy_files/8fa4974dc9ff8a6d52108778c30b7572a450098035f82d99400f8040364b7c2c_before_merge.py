    def __init__(self, debug_filename):
        self.debug_filename = debug_filename
        self.pending = []
        self.finished = set()