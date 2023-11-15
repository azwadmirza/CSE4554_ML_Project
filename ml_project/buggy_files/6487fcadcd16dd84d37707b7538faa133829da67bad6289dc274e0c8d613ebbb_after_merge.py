    def __init__(self, highlight_caret_scope=False):
        Panel.__init__(self)
        self._native_icons = False
        self._indicators_icons = (
            'folding.arrow_right_off',
            'folding.arrow_right_on',
            'folding.arrow_down_off',
            'folding.arrow_down_on'
        )
        self._block_nbr = -1
        self._highlight_caret = False
        self.highlight_caret_scope = highlight_caret_scope
        self._indic_size = 16
        #: the list of deco used to highlight the current fold region (
        #: surrounding regions are darker)
        self._scope_decos = []
        #: the list of folded blocs decorations
        self._block_decos = {}
        self.setMouseTracking(True)
        self.scrollable = True
        self._mouse_over_line = None
        self._current_scope = None
        self._prev_cursor = None
        self.context_menu = None
        self.action_collapse = None
        self.action_expand = None
        self.action_collapse_all = None
        self.action_expand_all = None
        self._original_background = None
        self._display_folding = False
        self._key_pressed = False
        self._highlight_runner = DelayJobRunner(delay=250)
        self.current_tree = IntervalTree()
        self.root = FoldingRegion(None, None)
        self.folding_regions = {}
        self.folding_status = {}
        self.folding_levels = {}
        self.folding_nesting = {}