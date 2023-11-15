    def __init__(self, plugin_class, module_path, parent):
        super().__init__()
        self.__plugins: Dict[str, T] = {}
        self.__classes: Dict[str, Type[T]] = {}
        self.__deps: Dict[str, str] = {}
        self.__cfls: Dict[str, str] = {}
        self.__loaded: List[str] = []
        self.parent = parent

        self.module_path = module_path
        self.plugin_class = plugin_class