    def __init__(self, context, func_ir, warnings):
        self.context = context
        self.blocks = func_ir.blocks
        self.generator_info = func_ir.generator_info
        self.func_id = func_ir.func_id
        self.func_ir = func_ir

        self.typevars = TypeVarMap()
        self.typevars.set_context(context)
        self.constraints = ConstraintNetwork()
        self.warnings = warnings

        # { index: mangled name }
        self.arg_names = {}
        #self.return_type = None
        # Set of assumed immutable globals
        self.assumed_immutables = set()
        # Track all calls and associated constraints
        self.calls = []
        # The inference result of the above calls
        self.calltypes = utils.UniqueDict()
        # Target var -> constraint with refine hook
        self.refine_map = {}

        if config.DEBUG or config.DEBUG_TYPEINFER:
            self.debug = TypeInferDebug(self)
        else:
            self.debug = NullDebug()

        self._skip_recursion = False