  def __init__(self,
               errorlog,
               options,
               loader,
               generate_unknowns=False,
               store_all_calls=False):
    """Construct a TypegraphVirtualMachine."""
    self.maximum_depth = None  # set by run_program() and analyze()
    self.errorlog = errorlog
    self.options = options
    self.python_version = options.python_version
    self.PY2 = self.python_version[0] == 2
    self.PY3 = self.python_version[0] == 3
    self.generate_unknowns = generate_unknowns
    self.store_all_calls = store_all_calls
    self.loader = loader
    self.frames = []  # The call stack of frames.
    self.functions_with_late_annotations = []
    self.functions_type_params_check = []
    self.concrete_classes = []
    self.frame = None  # The current frame.
    self.program = cfg.Program()
    self.root_cfg_node = self.program.NewCFGNode("root")
    self.program.entrypoint = self.root_cfg_node
    self.annotations_util = annotations_util.AnnotationsUtil(self)
    self.attribute_handler = attribute.AbstractAttributeHandler(self)
    self.matcher = matcher.AbstractMatcher(self)
    self.convert = convert.Converter(self)
    self.program.default_data = self.convert.unsolvable
    self.has_unknown_wildcard_imports = False
    self.callself_stack = []
    self.filename = None
    self.director = None
    self._analyzing = False  # Are we in self.analyze()?
    self.opcode_traces = []
    self._importing = False  # Are we importing another file?

    # Map from builtin names to canonical objects.
    self.special_builtins = {
        # The super() function.
        "super": self.convert.super_type,
        # The object type.
        "object": self.convert.object_type,
        # for more pretty branching tests.
        "__random__": self.convert.primitive_class_instances[bool],
        # for debugging
        "reveal_type": special_builtins.RevealType(self),
        # boolean values.
        "True": self.convert.true,
        "False": self.convert.false,
        "isinstance": special_builtins.IsInstance(self),
        "issubclass": special_builtins.IsSubclass(self),
        "hasattr": special_builtins.HasAttr(self),
        "callable": special_builtins.IsCallable(self),
        "abs": special_builtins.Abs(self),
        "next": special_builtins.Next(self),
        "open": special_builtins.Open(self),
        "property": special_builtins.Property(self),
        "staticmethod": special_builtins.StaticMethod(self),
        "classmethod": special_builtins.ClassMethod(self),
    }

    # Memoize which overlays are loaded.
    self.loaded_overlays = {}