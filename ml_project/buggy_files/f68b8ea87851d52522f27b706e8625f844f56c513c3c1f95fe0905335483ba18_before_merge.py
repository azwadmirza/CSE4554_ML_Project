    def __init__(self):
        EditorExtension.__init__(self)
        self.is_snippet_active = False
        self.active_snippet = -1
        self.node_number = 0
        self.index = None
        self.ast = None
        self.starting_position = None
        self.modification_lock = QMutex()
        self.event_lock = QMutex()
        self.node_position = {}
        self.snippets_map = {}
        self.undo_stack = []
        self.redo_stack = []
        if rtree_available:
            self.index = index.Index()