    def __init__(self, root_model, link, source, target=None, arg_overrides={}):
        self.root_model = root_model
        self.link = link
        self.source = source
        self.target = target
        self.arg_overrides = arg_overrides
        self.validate()
        specs = self._get_specs(link, source, target)
        for src_spec, tgt_spec, code in specs:
            self._init_callback(root_model, link, source, src_spec, target, tgt_spec, code)