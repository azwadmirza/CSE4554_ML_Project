    def __init__(self, data_dir: str,
                 lib_path: List[str],
                 ignore_prefix: str,
                 source_set: BuildSourceSet,
                 reports: Reports,
                 options: Options,
                 version_id: str,
                 plugin: Plugin,
                 errors: Errors) -> None:
        self.start_time = time.time()
        self.data_dir = data_dir
        self.errors = errors
        self.errors.set_ignore_prefix(ignore_prefix)
        self.lib_path = tuple(lib_path)
        self.source_set = source_set
        self.reports = reports
        self.options = options
        self.version_id = version_id
        self.modules = {}  # type: Dict[str, MypyFile]
        self.missing_modules = set()  # type: Set[str]
        self.plugin = plugin
        self.semantic_analyzer = SemanticAnalyzer(self.modules, self.missing_modules,
                                                  lib_path, self.errors, self.plugin)
        self.modules = self.semantic_analyzer.modules
        self.semantic_analyzer_pass3 = ThirdPass(self.modules, self.errors, self.semantic_analyzer)
        self.all_types = {}  # type: Dict[Expression, Type]
        self.indirection_detector = TypeIndirectionVisitor()
        self.stale_modules = set()  # type: Set[str]
        self.rechecked_modules = set()  # type: Set[str]
        self.plugin = plugin