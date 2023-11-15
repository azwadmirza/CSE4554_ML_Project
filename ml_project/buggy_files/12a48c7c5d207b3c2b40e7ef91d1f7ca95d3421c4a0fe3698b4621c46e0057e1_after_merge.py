    def __init__(self) -> None:
        # The stack of frames currently used.  These map
        # expr.literal_hash -- literals like 'foo.bar' --
        # to types. The last element of this list is the
        # top-most, current frame. Each earlier element
        # records the state as of when that frame was last
        # on top of the stack.
        self.frames = [Frame()]

        # For frames higher in the stack, we record the set of
        # Frames that can escape there, either by falling off
        # the end of the frame or by a loop control construct
        # or raised exception. The last element of self.frames
        # has no corresponding element in this list.
        self.options_on_return = []  # type: List[List[Frame]]

        # Maps expr.literal_hash] to get_declaration(expr)
        # for every expr stored in the binder
        self.declarations = Frame()
        # Set of other keys to invalidate if a key is changed, e.g. x -> {x.a, x[0]}
        # Whenever a new key (e.g. x.a.b) is added, we update this
        self.dependencies = {}  # type: Dict[Key, Set[Key]]

        # Whether the last pop changed the newly top frame on exit
        self.last_pop_changed = False

        self.try_frames = set()  # type: Set[int]
        self.break_frames = []  # type: List[int]
        self.continue_frames = []  # type: List[int]