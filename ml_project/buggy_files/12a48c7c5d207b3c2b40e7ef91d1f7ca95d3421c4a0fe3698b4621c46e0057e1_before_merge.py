    def __init__(self) -> None:
        # The set of frames currently used.  These map
        # expr.literal_hash -- literals like 'foo.bar' --
        # to types.
        self.frames = [Frame()]

        # For frames higher in the stack, we record the set of
        # Frames that can escape there
        self.options_on_return = []  # type: List[List[Frame]]

        # Maps expr.literal_hash] to get_declaration(expr)
        # for every expr stored in the binder
        self.declarations = Frame()
        # Set of other keys to invalidate if a key is changed, e.g. x -> {x.a, x[0]}
        # Whenever a new key (e.g. x.a.b) is added, we update this
        self.dependencies = {}  # type: Dict[Key, Set[Key]]

        # breaking_out is set to True on return/break/continue/raise
        # It is cleared on pop_frame() and placed in last_pop_breaking_out
        # Lines of code after breaking_out = True are unreachable and not
        # typechecked.
        self.breaking_out = False

        # Whether the last pop changed the newly top frame on exit
        self.last_pop_changed = False
        # Whether the last pop was necessarily breaking out, and couldn't fall through
        self.last_pop_breaking_out = False

        self.try_frames = set()  # type: Set[int]
        self.loop_frames = []  # type: List[int]