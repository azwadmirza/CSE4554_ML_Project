    def __init__(self, val, config):
        if is_nonstr_iter(val):
            self.val = set(val)
        else:
            self.val = set((val,))