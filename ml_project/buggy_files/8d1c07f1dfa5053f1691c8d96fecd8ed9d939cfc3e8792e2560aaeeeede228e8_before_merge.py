    def __init__(self, func_id):
        self.func_id = func_id
        self.arg_count = func_id.arg_count
        self.arg_names = func_id.arg_names
        self.loc = self.first_loc = ir.Loc.from_function_id(func_id)
        self.is_generator = func_id.is_generator

        # { inst offset : ir.Block }
        self.blocks = {}
        # { name: [definitions] } of local variables
        self.definitions = collections.defaultdict(list)