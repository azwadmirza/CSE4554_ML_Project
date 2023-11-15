    def __init__(self):
        """ initialize Jinja2 wrapper with extended set of filters"""
        if jinja2 is None:
            return
        self.lookup = jinja2.Environment()
        self.lookup.trim_blocks = True
        self.lookup.lstrip_blocks = True
        self.lookup.filters['tojson'] = json.dumps
        self.lookup.globals['enumerate'] = enumerate
        self.lookup.globals['isinstance'] = isinstance
        self.lookup.globals['tuple'] = tuple