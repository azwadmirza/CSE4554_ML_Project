    def __init__(self):
        # NB "actions" is an API, dep'd upon by pyramid_zcml's load_zcml func
        self.actions = []
        self._seen_files = set()