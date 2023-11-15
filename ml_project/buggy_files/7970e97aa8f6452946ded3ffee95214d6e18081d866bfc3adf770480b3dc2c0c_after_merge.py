    def __init__(self, typing_context):
        _load_global_helpers()

        self.address_size = utils.MACHINE_BITS
        self.typing_context = typing_context

        # A mapping of installed registries to their loaders
        self._registries = {}
        # Declarations loaded from registries and other sources
        self._defns = defaultdict(OverloadSelector)
        self._getattrs = defaultdict(OverloadSelector)
        self._setattrs = defaultdict(OverloadSelector)
        self._casts = OverloadSelector()
        self._get_constants = OverloadSelector()
        # Other declarations
        self._generators = {}
        self.special_ops = {}
        self.cached_internal_func = {}
        self._pid = None
        self._codelib_stack = []

        self._boundscheck = False

        self.data_model_manager = datamodel.default_manager

        # Initialize
        self.init()