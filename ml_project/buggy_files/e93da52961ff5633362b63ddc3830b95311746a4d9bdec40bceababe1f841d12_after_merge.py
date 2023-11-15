    def __init__(self, environment, parent, name, blocks):
        self.parent = parent
        self.vars = {}
        self.environment = environment
        self.eval_ctx = EvalContext(self.environment, name)
        self.exported_vars = set()
        self.name = name

        # create the initial mapping of blocks.  Whenever template inheritance
        # takes place the runtime will update this mapping with the new blocks
        # from the template.
        self.blocks = dict((k, [v]) for k, v in iteritems(blocks))

        # In case we detect the fast resolve mode we can set up an alias
        # here that bypasses the legacy code logic.
        if self._fast_resolve_mode:
            self.resolve_or_missing = MethodType(resolve_or_missing, self)