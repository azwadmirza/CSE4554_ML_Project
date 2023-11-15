    def __init__(self, document: nodes.document, builder: "TexinfoBuilder") -> None:
        super().__init__(document, builder)
        self.init_settings()

        self.written_ids = set()        # type: Set[str]
                                        # node names and anchors in output
        # node names and anchors that should be in output
        self.referenced_ids = set()     # type: Set[str]
        self.indices = []               # type: List[Tuple[str, str]]
                                        # (node name, content)
        self.short_ids = {}             # type: Dict[str, str]
                                        # anchors --> short ids
        self.node_names = {}            # type: Dict[str, str]
                                        # node name --> node's name to display
        self.node_menus = {}            # type: Dict[str, List[str]]
                                        # node name --> node's menu entries
        self.rellinks = {}              # type: Dict[str, List[str]]
                                        # node name --> (next, previous, up)

        self.collect_indices()
        self.collect_node_names()
        self.collect_node_menus()
        self.collect_rellinks()

        self.body = []                  # type: List[str]
        self.context = []               # type: List[str]
        self.descs = []                 # type: List[addnodes.desc]
        self.previous_section = None    # type: nodes.section
        self.section_level = 0
        self.seen_title = False
        self.next_section_ids = set()   # type: Set[str]
        self.escape_newlines = 0
        self.escape_hyphens = 0
        self.curfilestack = []          # type: List[str]
        self.footnotestack = []         # type: List[Dict[str, List[Union[collected_footnote, bool]]]]  # NOQA
        self.in_footnote = 0
        self.handled_abbrs = set()      # type: Set[str]
        self.colwidths = None           # type: List[int]